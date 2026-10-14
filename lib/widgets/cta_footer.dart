import 'package:flutter/material.dart';

import 'brand_mark.dart';
import 'responsive.dart';

/// Minimal homepage footer: one centred message and the project credit.
/// No links are shown until real pages exist for them.
class CtaFooter extends StatelessWidget {
  const CtaFooter({super.key});

  static const _navy = Color(0xFF0F1B3D);
  static const _muted = Color(0xFF5B6B85);
  static const _border = Color(0xFFE3E9F3);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: _border)),
      ),
      padding: const EdgeInsets.symmetric(vertical: 48),
      child: const PageWrap(
        child: Column(
          children: [
            BrandMark(size: 28),
            SizedBox(height: 16),
            Text(
              'More informed today. A more resilient tomorrow.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: _navy,
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 10),
            Text(
              '© 2026 Reflica · M.Tech research · GLA University',
              textAlign: TextAlign.center,
              style: TextStyle(color: _muted, fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }
}
