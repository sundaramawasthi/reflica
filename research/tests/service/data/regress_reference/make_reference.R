# Known-answer references for reflica_service regress@1 tests.
#
#   Rscript make_reference.R            (run from this directory)
#
# Uses only base R (stats, datasets). Writes <case>.csv (the data exactly as the
# service will read it) and <case>.json (values computed by R's lm() and by the
# textbook formulas below). Tests compare against these files, so R is not needed
# to run the tests. Regenerate only deliberately; record the R version used.
#
# Diagnostics are computed by hand here to pin their definitions:
#   Durbin-Watson   sum(diff(e)^2) / sum(e^2)
#   Jarque-Bera     n/6 * (S^2 + (K-3)^2/4), moments with divisor n; p = chi2(2)
#   Breusch-Pagan   Koenker (studentized): n * R^2 of e^2 on the predictors; df = k
#                   (as lmtest::bptest default)
#   RESET           F test adding fitted^2 (as lmtest::resettest(power = 2, type = "fitted"))
#   VIF             diag(solve(cor(X)))
#   condition no.   sqrt(kappa(cor(X), exact = TRUE)) = singular-value ratio of the
#                   centred, unit-norm predictor matrix

num <- function(x) {
  if (length(x) == 1 && is.na(x)) return("null")
  out <- ifelse(is.na(x), "null", sprintf("%.17g", x))
  out
}
arr <- function(x) paste0("[", paste(num(x), collapse = ", "), "]")
str_ <- function(x) paste0('"', x, '"')
strarr <- function(x) paste0("[", paste(str_(x), collapse = ", "), "]")
obj <- function(...) {
  kv <- list(...)
  paste0("{", paste(paste0(str_(names(kv)), ": ", unlist(kv)), collapse = ", "), "}")
}

reference <- function(name, data, target, predictors, intercept = TRUE, level = 0.95) {
  data <- data[, c(target, predictors)]
  write.csv(data, paste0(name, ".csv"), row.names = FALSE, na = "NA")
  rhs <- paste(c(if (intercept) "1" else "0", predictors), collapse = " + ")
  f <- as.formula(paste(target, "~", rhs))
  fit <- lm(f, data = data)                     # na.action = na.omit (listwise)
  s <- summary(fit)
  used <- match(names(residuals(fit)), rownames(data))  # 1-based data-row numbers
  cf <- s$coefficients
  ci <- confint(fit, level = level)
  e <- residuals(fit); n <- length(e); k <- length(predictors); p <- length(coef(fit))
  X <- as.matrix(data[used, predictors, drop = FALSE])
  m <- mean(e); S <- mean((e - m)^3) / mean((e - m)^2)^1.5; K <- mean((e - m)^4) / mean((e - m)^2)^2
  jb <- n / 6 * (S^2 + (K - 3)^2 / 4)
  dw <- sum(diff(e)^2) / sum(e^2)
  out <- list(r_version = str_(R.version.string), name = str_(name), target = str_(target),
              predictors = strarr(predictors), intercept = if (intercept) "true" else "false",
              confidence_level = num(level),
              n_rows = num(nrow(data)), n = num(n), df_resid = num(fit$df.residual),
              used_rows = arr(used),
              terms = strarr(rownames(cf)),
              estimate = arr(cf[, 1]), std_error = arr(cf[, 2]), t = arr(cf[, 3]), p = arr(cf[, 4]),
              ci_low = arr(ci[, 1]), ci_high = arr(ci[, 2]),
              sigma = num(s$sigma), r_squared = num(s$r.squared), adj_r_squared = num(s$adj.r.squared),
              f_statistic = num(s$fstatistic[1]), f_df1 = num(s$fstatistic[2]), f_df2 = num(s$fstatistic[3]),
              f_p = num(pf(s$fstatistic[1], s$fstatistic[2], s$fstatistic[3], lower.tail = FALSE)),
              log_likelihood = num(as.numeric(logLik(fit))), aic = num(AIC(fit)), bic = num(BIC(fit)),
              vcov = arr(as.vector(vcov(fit))),
              fitted = arr(fitted(fit)), residuals = arr(e),
              leverage = arr(hatvalues(fit)), cooks_distance = arr(cooks.distance(fit)),
              standardized_residuals = arr(rstandard(fit)), studentized_residuals = arr(rstudent(fit)),
              residual_quantiles = arr(quantile(e, c(0, .25, .5, .75, 1), type = 7)),
              durbin_watson = num(dw), jarque_bera = num(jb),
              jarque_bera_p = num(pchisq(jb, 2, lower.tail = FALSE)))
  if (intercept) {
    aux <- summary(lm(e^2 ~ X))
    bp <- n * aux$r.squared
    out$breusch_pagan <- num(bp); out$breusch_pagan_df <- num(k)
    out$breusch_pagan_p <- num(pchisq(bp, k, lower.tail = FALSE))
    out$standardized_coefficients <- arr(coef(fit)[-1] * apply(X, 2, sd) / sd(data[used, target]))
    if (k >= 2) {
      out$vif <- arr(diag(solve(cor(X))))
      out$condition_number <- num(sqrt(kappa(cor(X), exact = TRUE)))
    } else {
      out$vif <- arr(1); out$condition_number <- num(1)
    }
  }
  f2 <- fitted(fit)^2
  fit2 <- lm(update(f, . ~ . + f2), data = cbind(data[used, ], f2 = f2))
  rs <- anova(fit, fit2)
  out$reset_f <- num(rs$F[2]); out$reset_df1 <- num(rs$Df[2]); out$reset_df2 <- num(rs$Res.Df[2])
  out$reset_p <- num(rs[["Pr(>F)"]][2])
  writeLines(do.call(obj, out), paste0(name, ".json"))
}

reference("longley", longley, "Employed",
          c("GNP.deflator", "GNP", "Unemployed", "Armed.Forces", "Population", "Year"))
reference("mtcars", mtcars, "mpg", c("wt", "hp"))
reference("cars_no_intercept", cars, "dist", c("speed"), intercept = FALSE)
reference("airquality", airquality, "Ozone", c("Solar.R", "Wind", "Temp"), level = 0.90)

# Distribution functions used for p-values and confidence intervals.
grid <- rbind(
  expand.grid(kind = "t2", x = c(1e-3, 0.5, 1, 1.96, 2.5, 4, 8, 15, 40),
              df1 = c(1, 2, 3, 7, 30, 107, 1000, 99979), df2 = NA),
  expand.grid(kind = "f", x = c(1e-3, 0.3, 1, 2.5, 6, 20, 100),
              df1 = c(1, 2, 5, 20), df2 = c(1, 4, 13, 106, 5000)),
  expand.grid(kind = "chi2", x = c(1e-3, 0.5, 2, 5.99, 15, 40, 120),
              df1 = c(1, 2, 3, 6, 20, 100), df2 = NA),
  expand.grid(kind = "tq", x = c(0.5, 0.8, 0.9, 0.95, 0.99, 0.999),
              df1 = c(1, 2, 3, 7, 30, 107, 1000, 99979), df2 = NA))
grid$value <- suppressWarnings(with(grid, ifelse(kind == "t2", 2 * pt(x, df1, lower.tail = FALSE),
                         ifelse(kind == "f", pf(x, df1, df2, lower.tail = FALSE),
                         ifelse(kind == "chi2", pchisq(x, df1, lower.tail = FALSE),
                                qt((1 + x) / 2, df1))))))  # tq: x = confidence level; ifelse evaluates every branch
grid$value <- sprintf("%.17g", grid$value)
write.csv(grid, "distributions.csv", row.names = FALSE, na = "")
