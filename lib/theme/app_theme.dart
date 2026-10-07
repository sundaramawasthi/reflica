import 'package:flutter/material.dart';

class AppColors {
  // Light
  static const bg = Color(0xFFF6F3EC);
  static const surface = Color(0xFFFBFAF5);
  static const surface2 = Color(0xFFF0ECE0);
  static const ink = Color(0xFF0E1B22);
  static const ink2 = Color(0xFF2A3942);
  static const muted = Color(0xFF6B7A82);
  static const line = Color(0xFFDBD5C8);
  static const lineStrong = Color(0xFFB9B1A0);

  // Signal
  static const accent = Color(0xFF0C5A69);
  static const accent2 = Color(0xFF0E7686);
  static const amber = Color(0xFFB45A1B);
  static const amberSoft = Color(0xFFF0D9BC);
  static const sage = Color(0xFF2F7657);
  static const sageSoft = Color(0xFFCEE2D3);
  static const crimson = Color(0xFFA3341D);
  static const violet = Color(0xFF4A3E8E);
}

// System font fallbacks — Flutter walks these on each platform:
// - Android: Roboto (default), serif, monospace
// - iOS: .SF UI (default), Georgia, Menlo
// - Web: browser default, serif, monospace
// Using these keeps the UI legible everywhere without bundling fonts or any
// runtime network fetch (google_fonts was causing errors on offline Android).
const _displayStack = <String>['serif', 'Georgia', 'Times New Roman'];
const _sansStack = <String>[
  'Roboto',
  '-apple-system',
  'system-ui',
  'Segoe UI'
];
const _monoStack = <String>[
  'monospace',
  'ui-monospace',
  'Menlo',
  'Consolas',
];

class AppText {
  static TextStyle display({
    double size = 72,
    FontWeight weight = FontWeight.w400,
  }) =>
      TextStyle(
        fontFamily: _displayStack.first,
        fontFamilyFallback: _displayStack.sublist(1),
        fontSize: size,
        height: 1.04,
        letterSpacing: -size * 0.018,
        fontWeight: weight,
        color: AppColors.ink,
      );

  static TextStyle serif({
    double size = 24,
    FontWeight weight = FontWeight.w500,
    Color? color,
  }) =>
      TextStyle(
        fontFamily: _displayStack.first,
        fontFamilyFallback: _displayStack.sublist(1),
        fontSize: size,
        height: 1.2,
        letterSpacing: -size * 0.012,
        fontWeight: weight,
        color: color ?? AppColors.ink,
      );

  static TextStyle italicSerif({double size = 72, Color? color}) => TextStyle(
        fontFamily: _displayStack.first,
        fontFamilyFallback: _displayStack.sublist(1),
        fontSize: size,
        height: 1.04,
        letterSpacing: -size * 0.018,
        fontWeight: FontWeight.w500,
        fontStyle: FontStyle.italic,
        color: color ?? AppColors.accent,
      );

  static TextStyle body({
    double size = 16,
    FontWeight weight = FontWeight.w400,
    Color? color,
  }) =>
      TextStyle(
        fontFamily: _sansStack.first,
        fontFamilyFallback: _sansStack.sublist(1),
        fontSize: size,
        height: 1.55,
        letterSpacing: 0,
        fontWeight: weight,
        color: color ?? AppColors.ink2,
      );

  static TextStyle mono({
    double size = 12,
    FontWeight weight = FontWeight.w400,
    Color? color,
  }) =>
      TextStyle(
        fontFamily: _monoStack.first,
        fontFamilyFallback: _monoStack.sublist(1),
        fontSize: size,
        height: 1.5,
        fontWeight: weight,
        color: color ?? AppColors.muted,
      );

  static TextStyle eyebrow() => TextStyle(
        fontFamily: _monoStack.first,
        fontFamilyFallback: _monoStack.sublist(1),
        fontSize: 11,
        letterSpacing: 1.6,
        fontWeight: FontWeight.w500,
        color: AppColors.muted,
      );
}

class AppTheme {
  static ThemeData light() {
    final base = ThemeData.light(useMaterial3: true);
    return base.copyWith(
      scaffoldBackgroundColor: AppColors.bg,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.accent,
        brightness: Brightness.light,
        surface: AppColors.surface,
      ).copyWith(
        primary: AppColors.accent,
        onPrimary: Colors.white,
        secondary: AppColors.amber,
      ),
      textTheme: base.textTheme.apply(
        bodyColor: AppColors.ink,
        displayColor: AppColors.ink,
        fontFamily: _sansStack.first,
        fontFamilyFallback: _sansStack.sublist(1),
      ),
    );
  }
}
