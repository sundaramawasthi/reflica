import 'package:flutter/widgets.dart';

class Breakpoints {
  static const double sm = 560;
  static const double md = 900;
  static const double lg = 1180;
  static const double xl = 1240;
  static const double pageGutter = 24;
}

enum ScreenSize { phone, tablet, desktop, wide }

ScreenSize screenSizeOf(BuildContext context) {
  final w = MediaQuery.sizeOf(context).width;
  if (w < Breakpoints.sm) return ScreenSize.phone;
  if (w < Breakpoints.md) return ScreenSize.tablet;
  if (w < Breakpoints.lg) return ScreenSize.desktop;
  return ScreenSize.wide;
}

class PageWrap extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  const PageWrap({super.key, required this.child, this.padding});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: Breakpoints.xl),
        child: Padding(
          padding: padding ??
              const EdgeInsets.symmetric(horizontal: Breakpoints.pageGutter),
          child: child,
        ),
      ),
    );
  }
}
