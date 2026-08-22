import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// ============================================================
// RAAHAT DESIGN SYSTEM — CENTRALISED DESIGN TOKENS
// ============================================================
// This file is the single source of truth for every visual
// constant defined in the RAAHAT Design System specification.
// ============================================================

/// All colour tokens from the RAAHAT palette.
class RaahatColors {
  RaahatColors._();

  // ── Primary Emergency Red ──────────────────────────────────
  static const Color emergencyRed = Color(0xFFE8432E);
  static const Color redHover = Color(0xFFDC2626);
  static const Color redLight = Color(0xFFFEF2F2);
  static const Color redBorder = Color(0xFFFECACA);

  // ── Primary Blue ───────────────────────────────────────────
  static const Color primaryBlue = Color(0xFF1F4FD8);
  static const Color blueAlternate = Color(0xFF2563EB);
  static const Color blueHover = Color(0xFF1D4ED8);
  static const Color blueLight = Color(0xFFEFF6FF);
  static const Color blueBorder = Color(0xFFBFDBFE);

  // ── Status: Green ──────────────────────────────────────────
  static const Color green = Color(0xFF22C55E);
  static const Color verifiedGreen = Color(0xFF16A34A);

  // ── Status: Amber / Orange ─────────────────────────────────
  static const Color amber = Color(0xFFD97706);
  static const Color amberWarning = Color(0xFFF59E0B);
  static const Color orange = Color(0xFFEA580C);

  // ── Surfaces ───────────────────────────────────────────────
  static const Color canvasBackground = Color(0xFFFBFAF7);
  static const Color whiteCard = Color(0xFFFFFFFF);
  static const Color subtleBackground = Color(0xFFF4F2EC);
  static const Color mutedBackground = Color(0xFFF1F5F9);

  // ── Borders ────────────────────────────────────────────────
  static const Color border = Color(0xFFE2E8F0);
  static const Color strongBorder = Color(0xFFCBD5E1);

  // ── Text ───────────────────────────────────────────────────
  static const Color textPrimary = Color(0xFF14171C);
  static const Color textSecondary = Color(0xFF475569);
  static const Color textMuted = Color(0xFF64748B);
  static const Color textLight = Color(0xFF94A3B8);

  // ── Dark Console ───────────────────────────────────────────
  static const Color darkBackground = Color(0xFF14171C);
  static const Color darkSurface = Color(0xFF232629);
  static const Color darkElevated = Color(0xFF2C3137);
  static const Color darkBorder = Color(0xFF3A4047);
  static const Color darkText = Color(0xFFF4F2EC);
  static const Color darkMuted = Color(0xFF9AA0A8);
  static const Color darkGold = Color(0xFFD9A61C);
  static const Color darkVideoBackground = Color(0xFF0F172A);

  // ── Severity ───────────────────────────────────────────────
  static const Color severityCritical = Color(0xFFE8432E);
  static const Color severityHigh = Color(0xFFD97706);
  static const Color severityMedium = Color(0xFFF59E0B);
  static const Color severityLow = Color(0xFF10B981);

  // ── Live badge ─────────────────────────────────────────────
  static const Color liveBadgeBg = Color(0xFF166534);
  static const Color liveBadgeText = Color(0xFF4ADE80);

  /// Returns the correct colour for a severity string.
  static Color severityColor(String severity) {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return severityCritical;
      case 'HIGH':
        return severityHigh;
      case 'MEDIUM':
        return severityMedium;
      case 'LOW':
      case 'RESILIENCE':
        return severityLow;
      default:
        return textMuted;
    }
  }

  /// Light background for a given severity.
  static Color severityLightBg(String severity) {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return redLight;
      case 'HIGH':
        return const Color(0xFFFFFBEB);
      case 'MEDIUM':
        return const Color(0xFFFFFBEB);
      case 'LOW':
      case 'RESILIENCE':
        return const Color(0xFFECFDF5);
      default:
        return mutedBackground;
    }
  }
}

/// Spacing tokens on a 4dp base grid.
class RaahatSpacing {
  RaahatSpacing._();

  static const double xs2 = 2;
  static const double xs = 4;
  static const double sm = 8;
  static const double sm2 = 10;
  static const double md = 12;
  static const double md2 = 14;
  static const double base = 16;
  static const double lg = 20;
  static const double lg2 = 24;
  static const double xl = 28;
  static const double xl2 = 32;
  static const double xxl = 40;
  static const double xxxl = 60;
  static const double hero = 80;
}

/// Corner radius tokens.
class RaahatRadius {
  RaahatRadius._();

  static const double badge = 4;
  static const double button = 6;
  static const double card = 8;
  static const double input = 12;
  static const double mainCard = 16;
  static const double media = 20;
  static const double full = 999;
}

/// Elevation / shadow tokens translated to Flutter [BoxShadow].
class RaahatShadows {
  RaahatShadows._();

  /// Subtle card shadow: 0 2px 12px rgba(15,23,42,0.06)
  static const List<BoxShadow> card = [
    BoxShadow(
      color: Color(0x0F0F172A),
      blurRadius: 12,
      offset: Offset(0, 2),
    ),
  ];

  /// Prominent shadow: 0 8px 24px rgba(15,23,42,0.12)
  static const List<BoxShadow> prominent = [
    BoxShadow(
      color: Color(0x1F0F172A),
      blurRadius: 24,
      offset: Offset(0, 8),
    ),
  ];

  /// SOS red glow: 0 4px 20px rgba(239,68,68,0.30)
  static const List<BoxShadow> sosGlow = [
    BoxShadow(
      color: Color(0x4DEF4444),
      blurRadius: 20,
      offset: Offset(0, 4),
    ),
  ];
}

/// Typography helpers for the RAAHAT 3-font system.
///
/// - Display / Hero: Barlow Condensed
/// - Body / UI: Inter
/// - Mono / Telemetry: IBM Plex Mono
class RaahatTypography {
  RaahatTypography._();

  // ── Display (Barlow Condensed) ─────────────────────────────

  static TextStyle displayHero({
    double fontSize = 52,
    FontWeight fontWeight = FontWeight.w700,
    Color color = RaahatColors.textPrimary,
    double height = 1.1,
  }) =>
      GoogleFonts.barlowCondensed(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
        height: height,
        letterSpacing: -0.5,
      );

  static TextStyle displayH2({
    double fontSize = 48,
    FontWeight fontWeight = FontWeight.w700,
    Color color = RaahatColors.textPrimary,
  }) =>
      GoogleFonts.barlowCondensed(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
        height: 1.15,
      );

  static TextStyle displayH3({
    double fontSize = 34,
    FontWeight fontWeight = FontWeight.w600,
    Color color = RaahatColors.textPrimary,
  }) =>
      GoogleFonts.barlowCondensed(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
        height: 1.2,
      );

  // ── Body / UI (Inter) ──────────────────────────────────────

  static TextStyle cardTitle({
    Color color = RaahatColors.textPrimary,
  }) =>
      GoogleFonts.inter(
        fontSize: 18,
        fontWeight: FontWeight.w700,
        color: color,
        height: 1.35,
      );

  static TextStyle bodyLarge({
    Color color = RaahatColors.textPrimary,
    FontWeight fontWeight = FontWeight.w400,
  }) =>
      GoogleFonts.inter(
        fontSize: 19,
        fontWeight: fontWeight,
        color: color,
        height: 1.5,
      );

  static TextStyle bodyRegular({
    Color color = RaahatColors.textPrimary,
    FontWeight fontWeight = FontWeight.w400,
  }) =>
      GoogleFonts.inter(
        fontSize: 17,
        fontWeight: fontWeight,
        color: color,
        height: 1.5,
      );

  static TextStyle bodySmall({
    Color color = RaahatColors.textSecondary,
    FontWeight fontWeight = FontWeight.w400,
  }) =>
      GoogleFonts.inter(
        fontSize: 14,
        fontWeight: fontWeight,
        color: color,
        height: 1.45,
      );

  static TextStyle eyebrow({
    Color color = RaahatColors.textMuted,
    FontWeight fontWeight = FontWeight.w700,
  }) =>
      GoogleFonts.inter(
        fontSize: 13,
        fontWeight: fontWeight,
        color: color,
        height: 1.3,
        letterSpacing: 0.6,
      );

  static TextStyle buttonText({
    Color color = Colors.white,
    double fontSize = 16,
    FontWeight fontWeight = FontWeight.w600,
  }) =>
      GoogleFonts.inter(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
        height: 1.25,
      );

  static TextStyle navigation({
    Color color = RaahatColors.textMuted,
    FontWeight fontWeight = FontWeight.w500,
  }) =>
      GoogleFonts.inter(
        fontSize: 14,
        fontWeight: fontWeight,
        color: color,
      );

  static TextStyle metadata({
    Color color = RaahatColors.textMuted,
    FontWeight fontWeight = FontWeight.w500,
  }) =>
      GoogleFonts.inter(
        fontSize: 13,
        fontWeight: fontWeight,
        color: color,
        height: 1.3,
      );

  // ── Mono / Telemetry (IBM Plex Mono) ───────────────────────

  static TextStyle mono({
    double fontSize = 13,
    FontWeight fontWeight = FontWeight.w400,
    Color color = RaahatColors.darkText,
  }) =>
      GoogleFonts.ibmPlexMono(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
        height: 1.4,
      );

  static TextStyle monoBadge({
    Color color = RaahatColors.liveBadgeText,
    FontWeight fontWeight = FontWeight.w700,
  }) =>
      GoogleFonts.ibmPlexMono(
        fontSize: 11,
        fontWeight: fontWeight,
        color: color,
        height: 1.2,
      );
}
