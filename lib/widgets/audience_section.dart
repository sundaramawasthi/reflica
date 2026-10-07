import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../theme/app_theme.dart';
import 'responsive.dart';

const _brandBlue = Color(0xFF2E6FEB);

class AudienceSection extends StatelessWidget {
  const AudienceSection({super.key});

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final cols = switch (size) {
      ScreenSize.phone => 1,
      ScreenSize.tablet => 2,
      ScreenSize.desktop => 3,
      ScreenSize.wide => 5,
    };

    const items = [
      _AudItem(
        title: 'For Individuals',
        bullets: [
          'Study & exam planning',
          'Career and skill development',
          'Personal goals and planning',
          'Health and lifestyle decisions',
        ],
        more: 'Explore for Individuals',
        tint: _brandBlue,
        scene: _Scene.person,
        imageAsset: 'assets/images/audience/individual.jpg',
      ),
      _AudItem(
        title: 'For Organizations',
        bullets: [
          'Project and resource planning',
          'Operations and supply chain',
          'Risk and scenario analysis',
          'Team and task management',
        ],
        more: 'Explore for Organizations',
        tint: Color(0xFF2E8E6B),
        scene: _Scene.city,
        imageAsset: 'assets/images/audience/organization.svg',
      ),
      _AudItem(
        title: 'For Research Institutions',
        bullets: [
          'Research planning and tracking',
          'Data and evidence organization',
          'Experiment and resource planning',
          'Collaboration and publication',
        ],
        more: 'Explore for Research',
        tint: Color(0xFFB1472F),
        scene: _Scene.research,
        imageAsset: 'assets/images/audience/research.png',
      ),
      _AudItem(
        title: 'For Government',
        bullets: [
          'Disaster management',
          'Infrastructure and public services',
          'Policy and strategic planning',
          'Resource allocation',
        ],
        more: 'Explore for Government',
        tint: Color(0xFF7A5BE8),
        scene: _Scene.gov,
        imageAsset: 'assets/images/audience/government.png',
      ),
      _AudItem(
        title: 'For Disaster & Emergency',
        bullets: [
          'Real-time situation awareness',
          'Evacuation and relief planning',
          'Resource and logistics tracking',
          'Multi-agency coordination',
        ],
        more: 'Explore for Disaster Management',
        tint: Color(0xFFB45A1B),
        scene: _Scene.disaster,
        imageAsset: 'assets/images/audience/disaster.jpg',
      ),
    ];

    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(vertical: 72),
      child: PageWrap(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text(
              'Built for Every Goal, Every Scale',
              textAlign: TextAlign.center,
              style: AppText.serif(size: 36, weight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            Text(
              'The same intelligent core. Different needs. Real impact.',
              textAlign: TextAlign.center,
              style: AppText.body(size: 16, color: AppColors.muted),
            ),
            const SizedBox(height: 40),
            LayoutBuilder(builder: (context, c) {
              const gap = 20.0;
              final cardWidth =
                  ((c.maxWidth - (cols - 1) * gap) / cols).floorToDouble();
              return Wrap(
                spacing: gap,
                runSpacing: gap,
                alignment: WrapAlignment.center,
                children: items
                    .map((i) => SizedBox(
                          width: cardWidth,
                          child: _AudCard(item: i),
                        ))
                    .toList(),
              );
            }),
            const SizedBox(height: 56),
            const _OutcomeStrip(),
          ],
        ),
      ),
    );
  }
}

enum _Scene { person, city, research, gov, disaster }

class _AudItem {
  final String title;
  final List<String> bullets;
  final String more;
  final Color tint;
  final _Scene scene;
  final String? imageAsset;
  const _AudItem({
    required this.title,
    required this.bullets,
    required this.more,
    required this.tint,
    required this.scene,
    this.imageAsset,
  });
}

class _AudCard extends StatefulWidget {
  final _AudItem item;
  const _AudCard({required this.item});

  @override
  State<_AudCard> createState() => _AudCardState();
}

class _AudCardState extends State<_AudCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        transform: Matrix4.translationValues(0, _hover ? -4 : 0, 0),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(
            color: _hover
                ? item.tint.withValues(alpha: 0.4)
                : AppColors.line,
          ),
          borderRadius: BorderRadius.circular(18),
          boxShadow: _hover
              ? [
                  BoxShadow(
                    color: item.tint.withValues(alpha: 0.18),
                    blurRadius: 32,
                    offset: const Offset(0, 12),
                    spreadRadius: -10,
                  ),
                ]
              : [
                  BoxShadow(
                    color: AppColors.ink.withValues(alpha: 0.03),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            AspectRatio(
              aspectRatio: 4 / 2.6,
              child: item.imageAsset != null
                  ? _ImageHeader(asset: item.imageAsset!, tint: item.tint)
                  : _SceneCanvas(scene: item.scene, tint: item.tint),
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: item.tint.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    alignment: Alignment.center,
                    child: Icon(
                      _iconFor(item.scene),
                      color: item.tint,
                      size: 18,
                    ),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    item.title,
                    style: AppText.serif(size: 18, weight: FontWeight.w600),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 12),
                  ...item.bullets.map(
                    (b) => Padding(
                      padding: const EdgeInsets.only(bottom: 7),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Container(
                              width: 4,
                              height: 4,
                              decoration: BoxDecoration(
                                color: item.tint,
                                shape: BoxShape.circle,
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              b,
                              style: AppText.body(
                                size: 13,
                                color: AppColors.ink2,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  AnimatedDefaultTextStyle(
                    duration: const Duration(milliseconds: 150),
                    style: AppText.body(
                      size: 13,
                      weight: FontWeight.w600,
                      color: item.tint,
                    ),
                    child: Row(
                      children: [
                        Flexible(
                          child: Text(
                            item.more,
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                          ),
                        ),
                        AnimatedPadding(
                          duration: const Duration(milliseconds: 150),
                          padding: EdgeInsets.only(left: _hover ? 8 : 4),
                          child: Icon(
                            Icons.arrow_forward,
                            size: 14,
                            color: item.tint,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _iconFor(_Scene s) {
    switch (s) {
      case _Scene.person:
        return Icons.person_outline;
      case _Scene.city:
        return Icons.business_outlined;
      case _Scene.research:
        return Icons.science_outlined;
      case _Scene.gov:
        return Icons.account_balance_outlined;
      case _Scene.disaster:
        return Icons.waves_outlined;
    }
  }
}

class _ImageHeader extends StatelessWidget {
  final String asset;
  final Color tint;
  const _ImageHeader({required this.asset, required this.tint});

  @override
  Widget build(BuildContext context) {
    final isSvg = asset.toLowerCase().endsWith('.svg');
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color.lerp(tint, Colors.white, 0.88)!,
            Color.lerp(tint, Colors.white, 0.72)!,
          ],
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: isSvg
            ? SvgPicture.asset(
                asset,
                fit: BoxFit.contain,
                placeholderBuilder: (_) => Center(
                  child: Icon(
                    Icons.image_outlined,
                    color: tint.withValues(alpha: 0.5),
                    size: 36,
                  ),
                ),
              )
            : Image.asset(
                asset,
                fit: BoxFit.contain,
                errorBuilder: (ctx, err, stack) => Center(
                  child: Icon(
                    Icons.image_outlined,
                    color: tint.withValues(alpha: 0.5),
                    size: 36,
                  ),
                ),
              ),
      ),
    );
  }
}

class _SceneCanvas extends StatelessWidget {
  final _Scene scene;
  final Color tint;
  const _SceneCanvas({required this.scene, required this.tint});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _ScenePainter(scene: scene, tint: tint),
      child: Container(),
    );
  }
}

class _ScenePainter extends CustomPainter {
  final _Scene scene;
  final Color tint;
  _ScenePainter({required this.scene, required this.tint});

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // ambient background per scene
    final bgTop = Color.lerp(tint, Colors.white, 0.78)!;
    final bgBottom = Color.lerp(tint, Colors.white, 0.55)!;
    final bgPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [bgTop, bgBottom],
      ).createShader(Rect.fromLTWH(0, 0, w, h));
    canvas.drawRect(Rect.fromLTWH(0, 0, w, h), bgPaint);

    switch (scene) {
      case _Scene.person:
        _paintPerson(canvas, w, h);
        break;
      case _Scene.city:
        _paintCity(canvas, w, h);
        break;
      case _Scene.research:
        _paintResearch(canvas, w, h);
        break;
      case _Scene.gov:
        _paintGov(canvas, w, h);
        break;
      case _Scene.disaster:
        _paintDisaster(canvas, w, h);
        break;
    }
  }

  // ----- scenes -----

  void _paintPerson(Canvas canvas, double w, double h) {
    // desk + laptop silhouette, warm interior
    final deskColor = Color.lerp(tint, Colors.white, 0.3)!;
    final personColor = Color.lerp(tint, const Color(0xFF1C2C3B), 0.5)!;

    // ambient light orb (window)
    canvas.drawCircle(
      Offset(w * 0.78, h * 0.25),
      w * 0.22,
      Paint()..color = Colors.white.withValues(alpha: 0.65),
    );

    // desk
    final desk = Path()
      ..moveTo(0, h * 0.78)
      ..lineTo(w, h * 0.78)
      ..lineTo(w, h)
      ..lineTo(0, h)
      ..close();
    canvas.drawPath(desk, Paint()..color = deskColor);

    // laptop
    final lap = Rect.fromLTWH(w * 0.30, h * 0.56, w * 0.4, h * 0.22);
    canvas.drawRRect(
      RRect.fromRectAndRadius(lap, const Radius.circular(4)),
      Paint()..color = const Color(0xFF2A3B4A),
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(w * 0.32, h * 0.58, w * 0.36, h * 0.18),
        const Radius.circular(2),
      ),
      Paint()..color = tint.withValues(alpha: 0.6),
    );

    // person silhouette (torso + head)
    canvas.drawCircle(
      Offset(w * 0.5, h * 0.26),
      w * 0.07,
      Paint()..color = personColor,
    );
    final torso = Path()
      ..moveTo(w * 0.35, h * 0.65)
      ..quadraticBezierTo(w * 0.5, h * 0.3, w * 0.65, h * 0.65)
      ..lineTo(w * 0.6, h * 0.72)
      ..lineTo(w * 0.4, h * 0.72)
      ..close();
    canvas.drawPath(torso, Paint()..color = personColor);
  }

  void _paintCity(Canvas canvas, double w, double h) {
    // skyline
    final buildings = [
      Rect.fromLTWH(w * 0.05, h * 0.35, w * 0.14, h * 0.65),
      Rect.fromLTWH(w * 0.20, h * 0.20, w * 0.18, h * 0.80),
      Rect.fromLTWH(w * 0.40, h * 0.30, w * 0.12, h * 0.70),
      Rect.fromLTWH(w * 0.53, h * 0.15, w * 0.17, h * 0.85),
      Rect.fromLTWH(w * 0.71, h * 0.40, w * 0.12, h * 0.60),
      Rect.fromLTWH(w * 0.84, h * 0.28, w * 0.14, h * 0.72),
    ];
    final shades = [
      Color.lerp(tint, Colors.white, 0.55)!,
      Color.lerp(tint, Colors.white, 0.35)!,
      Color.lerp(tint, Colors.white, 0.45)!,
      Color.lerp(tint, Colors.white, 0.25)!,
      Color.lerp(tint, Colors.white, 0.5)!,
      Color.lerp(tint, Colors.white, 0.35)!,
    ];
    for (int i = 0; i < buildings.length; i++) {
      canvas.drawRect(buildings[i], Paint()..color = shades[i]);
      // window grid
      final b = buildings[i];
      final cols = (b.width / 10).floor().clamp(2, 5);
      final rows = (b.height / 14).floor().clamp(3, 10);
      for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
          final x = b.left + 4 + c * (b.width - 6) / cols;
          final y = b.top + 6 + r * (b.height - 8) / rows;
          canvas.drawRect(
            Rect.fromLTWH(x, y, 3, 4),
            Paint()..color = Colors.white.withValues(alpha: 0.6),
          );
        }
      }
    }
  }

  void _paintResearch(Canvas canvas, double w, double h) {
    // columned research building
    final body =
        Color.lerp(tint, Colors.white, 0.6)!;
    final roof = Path()
      ..moveTo(w * 0.5, h * 0.1)
      ..lineTo(w * 0.9, h * 0.35)
      ..lineTo(w * 0.1, h * 0.35)
      ..close();
    canvas.drawPath(roof, Paint()..color = body);
    canvas.drawRect(
      Rect.fromLTWH(w * 0.1, h * 0.35, w * 0.8, h * 0.07),
      Paint()..color = body,
    );
    // columns
    for (int i = 0; i < 6; i++) {
      final x = w * (0.15 + i * 0.13);
      canvas.drawRect(
        Rect.fromLTWH(x, h * 0.42, w * 0.05, h * 0.5),
        Paint()..color = body,
      );
    }
    // base
    canvas.drawRect(
      Rect.fromLTWH(w * 0.08, h * 0.92, w * 0.84, h * 0.08),
      Paint()..color = body,
    );
    // flag
    canvas.drawLine(
      Offset(w * 0.5, h * 0.1),
      Offset(w * 0.5, h * 0.03),
      Paint()
        ..color = tint
        ..strokeWidth = 1.5,
    );
    canvas.drawRect(
      Rect.fromLTWH(w * 0.5, h * 0.03, w * 0.04, h * 0.04),
      Paint()..color = tint,
    );
  }

  void _paintGov(Canvas canvas, double w, double h) {
    // dome capitol
    final body = Color.lerp(tint, Colors.white, 0.55)!;
    final dome = Rect.fromCircle(center: Offset(w * 0.5, h * 0.35), radius: w * 0.18);
    canvas.drawArc(dome, math.pi, math.pi, true, Paint()..color = body);
    canvas.drawLine(
      Offset(w * 0.5, h * 0.05),
      Offset(w * 0.5, h * 0.15),
      Paint()..color = tint..strokeWidth = 1.5,
    );
    // main building
    canvas.drawRect(
      Rect.fromLTWH(w * 0.08, h * 0.4, w * 0.84, h * 0.12),
      Paint()..color = body,
    );
    // columns
    for (int i = 0; i < 7; i++) {
      final x = w * (0.12 + i * 0.11);
      canvas.drawRect(
        Rect.fromLTWH(x, h * 0.52, w * 0.055, h * 0.4),
        Paint()..color = body,
      );
    }
    canvas.drawRect(
      Rect.fromLTWH(w * 0.06, h * 0.92, w * 0.88, h * 0.08),
      Paint()..color = body,
    );
  }

  void _paintDisaster(Canvas canvas, double w, double h) {
    // river + boats + rising water
    final waterDeep = Color.lerp(tint, const Color(0xFF2C3E50), 0.4)!;
    final waterMid = Color.lerp(tint, Colors.white, 0.3)!;

    // sky mountains in background
    final mountain = Path()
      ..moveTo(0, h * 0.5)
      ..lineTo(w * 0.3, h * 0.15)
      ..lineTo(w * 0.55, h * 0.4)
      ..lineTo(w * 0.8, h * 0.1)
      ..lineTo(w, h * 0.45)
      ..lineTo(w, h * 0.55)
      ..lineTo(0, h * 0.55)
      ..close();
    canvas.drawPath(mountain, Paint()..color = tint.withValues(alpha: 0.3));

    // water
    final water = Path()
      ..moveTo(0, h * 0.55)
      ..quadraticBezierTo(w * 0.25, h * 0.5, w * 0.5, h * 0.57)
      ..quadraticBezierTo(w * 0.75, h * 0.65, w, h * 0.56)
      ..lineTo(w, h)
      ..lineTo(0, h)
      ..close();
    canvas.drawPath(water, Paint()..color = waterMid);
    final waterFront = Path()
      ..moveTo(0, h * 0.75)
      ..quadraticBezierTo(w * 0.3, h * 0.7, w * 0.6, h * 0.78)
      ..quadraticBezierTo(w * 0.85, h * 0.85, w, h * 0.78)
      ..lineTo(w, h)
      ..lineTo(0, h)
      ..close();
    canvas.drawPath(waterFront, Paint()..color = waterDeep);

    // boat 1
    _boat(canvas, w * 0.3, h * 0.68, w * 0.18, h * 0.08);
    // boat 2
    _boat(canvas, w * 0.65, h * 0.72, w * 0.22, h * 0.09);
  }

  void _boat(Canvas canvas, double x, double y, double bw, double bh) {
    final boat = Path()
      ..moveTo(x, y)
      ..lineTo(x + bw, y)
      ..lineTo(x + bw * 0.85, y + bh)
      ..lineTo(x + bw * 0.15, y + bh)
      ..close();
    canvas.drawPath(boat, Paint()..color = const Color(0xFFD48842));
    // orange outline for distinction
    canvas.drawPath(
      boat,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.2
        ..color = const Color(0xFF8E4517),
    );
    // tiny people
    for (int i = 0; i < 3; i++) {
      canvas.drawCircle(
        Offset(x + bw * (0.3 + i * 0.2), y - bh * 0.1),
        bh * 0.12,
        Paint()..color = const Color(0xFFEE7B35),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _ScenePainter old) =>
      old.scene != scene || old.tint != tint;
}

class _OutcomeStrip extends StatelessWidget {
  const _OutcomeStrip();

  @override
  Widget build(BuildContext context) {
    const parts = [
      ('Better information', _brandBlue),
      ('Smarter reasoning', Color(0xFF2E8E6B)),
      ('Adaptive planning', Color(0xFF7A5BE8)),
      ('More reliable decisions', AppColors.ink),
    ];
    return LayoutBuilder(builder: (context, c) {
      final tight = c.maxWidth < 720;
      final items = <Widget>[];
      for (int i = 0; i < parts.length; i++) {
        items.add(Text(
          parts[i].$1,
          style: AppText.body(
            size: 15,
            weight: FontWeight.w600,
            color: parts[i].$2,
          ),
        ));
        if (i < parts.length - 1) {
          items.add(Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14),
            child: Text(
              i == parts.length - 2 ? '=' : '+',
              style: AppText.body(
                size: 15,
                weight: FontWeight.w400,
                color: AppColors.muted,
              ),
            ),
          ));
        }
      }
      return Container(
        padding: const EdgeInsets.only(top: 24),
        decoration: const BoxDecoration(
          border: Border(top: BorderSide(color: AppColors.line)),
        ),
        child: tight
            ? Column(
                children: [
                  for (int i = 0; i < items.length; i++)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: items[i],
                    ),
                ],
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: items,
              ),
      );
    });
  }
}
