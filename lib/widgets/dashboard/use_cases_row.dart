import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../theme/app_theme.dart';
import '../responsive.dart';

class UseCase {
  final String title;
  final String desc;
  final IconData icon;
  final Color tint;
  final String imageAsset;
  const UseCase(this.title, this.desc, this.icon, this.tint, this.imageAsset);
}

const useCases = <UseCase>[
  UseCase(
    'Personal',
    'Study, career, goals, finances and life decisions.',
    Icons.person_outline,
    AppColors.accent,
    'assets/images/audience/individual.jpg',
  ),
  UseCase(
    'Organisations',
    'Project planning, operations, resources and risk management.',
    Icons.business_outlined,
    AppColors.sage,
    'assets/images/audience/organization.svg',
  ),
  UseCase(
    'Government',
    'Disaster management, public services, infrastructure, policy and more.',
    Icons.account_balance_outlined,
    AppColors.violet,
    'assets/images/audience/government.png',
  ),
  UseCase(
    'Research & Academia',
    'Research planning, literature, experiments and collaboration.',
    Icons.science_outlined,
    AppColors.amber,
    'assets/images/audience/research.png',
  ),
  UseCase(
    'Disaster',
    'Real-time situation awareness, evacuation, relief and multi-agency coordination.',
    Icons.waves_outlined,
    AppColors.crimson,
    'assets/images/audience/disaster.jpg',
  ),
];

class UseCasesRow extends StatelessWidget {
  const UseCasesRow({super.key});

  @override
  Widget build(BuildContext context) {
    final cols = switch (screenSizeOf(context)) {
      ScreenSize.phone => 1,
      ScreenSize.tablet => 2,
      ScreenSize.desktop => 3,
      ScreenSize.wide => 5,
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'Explore Use Cases',
              style: AppText.serif(size: 22, weight: FontWeight.w500),
            ),
            const Spacer(),
            Text(
              'View all use cases  →',
              style: AppText.body(
                size: 13,
                weight: FontWeight.w500,
                color: AppColors.accent,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          'See how Reflica can help in different scenarios.',
          style: AppText.body(size: 13, color: AppColors.muted),
        ),
        const SizedBox(height: 20),
        LayoutBuilder(builder: (context, c) {
          const gap = 14.0;
          final cardWidth =
              ((c.maxWidth - (cols - 1) * gap) / cols).floorToDouble();
          return Wrap(
            spacing: gap,
            runSpacing: gap,
            alignment: WrapAlignment.start,
            children: useCases
                .map(
                  (u) => SizedBox(
                    width: cardWidth,
                    child: _UseCaseCard(uc: u),
                  ),
                )
                .toList(),
          );
        }),
      ],
    );
  }
}

class _UseCaseCard extends StatefulWidget {
  final UseCase uc;
  const _UseCaseCard({required this.uc});

  @override
  State<_UseCaseCard> createState() => _UseCaseCardState();
}

class _UseCaseCardState extends State<_UseCaseCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final uc = widget.uc;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        transform: Matrix4.translationValues(0, _hover ? -3 : 0, 0),
        decoration: BoxDecoration(
          color: uc.tint.withValues(alpha: 0.08),
          border: Border.all(
            color: _hover
                ? uc.tint.withValues(alpha: 0.5)
                : uc.tint.withValues(alpha: 0.2),
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Image panel
            AspectRatio(
              aspectRatio: 16 / 9,
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Color.lerp(uc.tint, Colors.white, 0.9)!,
                      Color.lerp(uc.tint, Colors.white, 0.75)!,
                    ],
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(8),
                  child: _UseCaseImage(asset: uc.imageAsset, tint: uc.tint),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 36,
                        height: 36,
                        decoration: BoxDecoration(
                          color: uc.tint.withValues(alpha: 0.18),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        alignment: Alignment.center,
                        child: Icon(uc.icon, color: uc.tint, size: 20),
                      ),
                      const Spacer(),
                      Container(
                        width: 28,
                        height: 28,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          border: Border.all(
                            color: uc.tint.withValues(alpha: 0.3),
                          ),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        alignment: Alignment.center,
                        child: Icon(Icons.arrow_forward,
                            size: 14, color: uc.tint),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Text(
                    uc.title,
                    style: AppText.serif(size: 18, weight: FontWeight.w500),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    uc.desc,
                    style: AppText.body(size: 13, color: AppColors.ink2),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _UseCaseImage extends StatelessWidget {
  final String asset;
  final Color tint;
  const _UseCaseImage({required this.asset, required this.tint});

  @override
  Widget build(BuildContext context) {
    final isSvg = asset.toLowerCase().endsWith('.svg');
    final fallback = Center(
      child: Icon(
        Icons.image_outlined,
        color: tint.withValues(alpha: 0.5),
        size: 28,
      ),
    );
    if (isSvg) {
      return SvgPicture.asset(
        asset,
        fit: BoxFit.contain,
        placeholderBuilder: (_) => fallback,
      );
    }
    return Image.asset(
      asset,
      fit: BoxFit.contain,
      errorBuilder: (_, _, _) => fallback,
    );
  }
}
