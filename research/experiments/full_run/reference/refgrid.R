.libPaths(c("Rlib", .libPaths())); suppressMessages(library(contingencytables))
tabs <- list()
for (N in c(1, 2, 3, 5, 12)) for (a in 0:N) for (b in 0:(N - a)) for (c in 0:(N - a - b)) tabs[[length(tabs) + 1]] <- c(a, b, c, N - a - b - c)
set.seed(20261010)
for (i in 1:400) { p <- runif(4); p <- p / sum(p); tabs[[length(tabs) + 1]] <- as.vector(rmultinom(1, 63, p)) }
edge <- list(c(0,0,0,63), c(63,0,0,0), c(0,63,0,0), c(0,0,63,0), c(0,1,0,62), c(62,0,1,0), c(31,1,1,30), c(0,32,31,0), c(55,8,0,0), c(0,0,8,55), c(60,3,0,0), c(58,0,5,0), c(1,30,30,2))
tabs <- c(tabs, edge)
g <- function(f, m) tryCatch(unlist(unclass(f(m))[c("lower","upper")]), error = function(e) c(NA, NA))
rows <- lapply(tabs, function(v) {
  m <- matrix(c(v[1], v[3], v[2], v[4]), 2)   # rows = first method (yes, no); n12 = b, n21 = c
  c(v, g(Newcombe_square_and_add_CI_paired_2x2, m), g(Tango_asymptotic_score_CI_paired_2x2, m),
    g(Wald_CI_AgrestiMin_paired_2x2, m), g(Wald_CI_BonettPrice_paired_2x2, m),
    tryCatch(unclass(McNemar_exact_cond_test_paired_2x2(m))$Pvalue, error = function(e) NA),
    tryCatch(unclass(McNemar_midP_test_paired_2x2(m))$midP, error = function(e) NA))
})
out <- do.call(rbind, rows)
colnames(out) <- c("a","b","c","d","nc_lo","nc_hi","ta_lo","ta_hi","am_lo","am_hi","bp_lo","bp_hi","p_exact","p_midp")
write.csv(out, "refgrid.csv", row.names = FALSE)
cp <- t(sapply(0:63, function(k) c(k, binom.test(k, 63)$conf.int, prop.test(k, 63, correct = FALSE)$conf.int)))
colnames(cp) <- c("k","cp_lo","cp_hi","w_lo","w_hi"); write.csv(cp, "refcp.csv", row.names = FALSE)
cat(nrow(out), "tables;", sum(is.na(out)), "NA cells\n")
# qt reference (added in v0.6): write.csv(data.frame(df=1:100, q975=qt(0.975, 1:100)), "refqt.csv")
