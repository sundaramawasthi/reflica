import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../widgets/app_top_bar.dart';
import '../widgets/audience_section.dart';
import '../widgets/cta_footer.dart';
import '../widgets/evidence_section.dart';
import '../widgets/hero_section.dart';
import '../widgets/input_modes_section.dart';
import '../widgets/living_loop_section.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _scroll = ScrollController();
  bool _scrolled = false;

  @override
  void initState() {
    super.initState();
    _scroll.addListener(() {
      final s = _scroll.offset > 8;
      if (s != _scrolled) setState(() => _scrolled = s);
    });
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      body: Stack(
        children: [
          Positioned.fill(
            child: SingleChildScrollView(
              controller: _scroll,
              child: Column(
                children: const [
                  SizedBox(height: 72),
                  // 1 · Headline + mind-map preview
                  HeroSection(),
                  // 2 · "Living loop" — what makes Reflica alive
                  LivingLoopSection(),
                  // 3 · All 7 input modes, one typed graph
                  InputModesSection(),
                  // 4 · Audience — one engine for five user classes
                  AudienceSection(),
                  // 5 · Five evidence types the system distinguishes
                  EvidenceSection(),
                  // 6 · CTA + footer
                  CtaFooter(),
                ],
              ),
            ),
          ),
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: AppTopBar(elevated: _scrolled),
          ),
        ],
      ),
    );
  }
}
