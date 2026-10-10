import 'package:flutter/material.dart';

import '../../graph/graph1.dart';
import '../../theme/app_theme.dart';

/// Small rounded label used for kinds, basis and certainty.
class GraphChip extends StatelessWidget {
  final String text;
  final Color color;
  final Color? fill;
  final IconData? icon;
  const GraphChip(this.text, {super.key, required this.color, this.fill, this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: fill ?? color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        if (icon != null) ...[Icon(icon, size: 12, color: color), const SizedBox(width: 4)],
        Text(text, style: AppText.mono(size: 11, color: color, weight: FontWeight.w600)),
      ]),
    );
  }
}

Color basisColor(Basis b) => switch (b) {
      Basis.sourceQuoted => AppColors.sage,
      Basis.userStated => AppColors.accent,
      Basis.computed => AppColors.violet,
      Basis.llmInferred => AppColors.amber,
      Basis.legacyUnverified => AppColors.muted,
    };

IconData basisIcon(Basis b) => switch (b) {
      Basis.sourceQuoted => Icons.format_quote,
      Basis.userStated => Icons.person_outline,
      Basis.computed => Icons.functions,
      Basis.llmInferred => Icons.auto_awesome_outlined,
      Basis.legacyUnverified => Icons.help_outline,
    };

class BasisChip extends StatelessWidget {
  final Basis basis;
  const BasisChip(this.basis, {super.key});

  @override
  Widget build(BuildContext context) =>
      GraphChip(basisLabel(basis), color: basisColor(basis), icon: basisIcon(basis));
}

class KindChip extends StatelessWidget {
  final String kind;
  const KindChip(this.kind, {super.key});

  @override
  Widget build(BuildContext context) => GraphChip(kind.toUpperCase(), color: AppColors.ink2);
}

/// Confirmed = stated in a source or by the researcher; inferred = suggested only.
class CertaintyChip extends StatelessWidget {
  final bool confirmed;
  final String confirmedText;
  final String uncertainText;
  const CertaintyChip(this.confirmed,
      {super.key, this.confirmedText = 'confirmed', this.uncertainText = 'inferred'});

  @override
  Widget build(BuildContext context) => confirmed
      ? GraphChip(confirmedText, color: AppColors.sage, icon: Icons.check)
      : GraphChip(uncertainText, color: AppColors.amber, icon: Icons.help_outline);
}

class QuoteBlock extends StatelessWidget {
  final String quote;
  const QuoteBlock(this.quote, {super.key});

  @override
  Widget build(BuildContext context) => Container(
        margin: const EdgeInsets.only(top: 6),
        padding: const EdgeInsets.fromLTRB(10, 6, 10, 6),
        decoration: const BoxDecoration(
          border: Border(left: BorderSide(color: AppColors.sage, width: 3)),
          color: AppColors.surface2,
        ),
        child: Text('“$quote”',
            style: AppText.body(size: 13, color: AppColors.ink2).copyWith(fontStyle: FontStyle.italic)),
      );
}
