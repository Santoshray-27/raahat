import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:raahat/core/theme/design_tokens.dart';

/// Centralized application theme for RAAHAT emergency assistance app.
/// Applies the RAAHAT Design System: colours, typography, spacing, radii, and shadows.
class AppTheme {
  AppTheme._();

  // ── Legacy colour accessors (kept for backward-compatibility) ───────────
  // Existing screens reference these via AppTheme.primaryColor etc.
  // We redirect them to the design-system palette so screens that
  // haven't been updated yet still compile and look consistent.

  static const Color primaryColor = RaahatColors.primaryBlue;
  static const Color secondaryColor = RaahatColors.blueAlternate;
  static const Color backgroundColor = RaahatColors.canvasBackground;
  static const Color surfaceColor = RaahatColors.whiteCard;

  static const Color errorColor = RaahatColors.emergencyRed;
  static const Color warningColor = RaahatColors.amberWarning;

  static const Color textPrimary = RaahatColors.textPrimary;
  static const Color textSecondary = RaahatColors.textSecondary;
  static const Color borderColor = RaahatColors.border;

  /// Light ThemeData following the RAAHAT Design System.
  static ThemeData get lightTheme {
    final ColorScheme colorScheme = ColorScheme.light(
      primary: RaahatColors.primaryBlue,
      onPrimary: Colors.white,
      primaryContainer: RaahatColors.blueLight,
      onPrimaryContainer: RaahatColors.primaryBlue,
      secondary: RaahatColors.blueAlternate,
      onSecondary: Colors.white,
      secondaryContainer: RaahatColors.blueLight,
      onSecondaryContainer: RaahatColors.primaryBlue,
      surface: RaahatColors.whiteCard,
      onSurface: RaahatColors.textPrimary,
      surfaceContainerHighest: RaahatColors.subtleBackground,
      onSurfaceVariant: RaahatColors.textSecondary,
      error: RaahatColors.emergencyRed,
      onError: Colors.white,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: RaahatColors.canvasBackground,

      // AppBar ────────────────────────────────────────────────────
      appBarTheme: AppBarTheme(
        backgroundColor: RaahatColors.whiteCard,
        foregroundColor: RaahatColors.textPrimary,
        elevation: 0,
        centerTitle: false,
        surfaceTintColor: Colors.transparent,
        iconTheme: const IconThemeData(color: RaahatColors.textPrimary),
        titleTextStyle: GoogleFonts.inter(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: RaahatColors.textPrimary,
          letterSpacing: -0.3,
        ),
      ),

      // Elevated Buttons ──────────────────────────────────────────
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: RaahatColors.primaryBlue,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 52),
          padding:
              const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(RaahatRadius.button),
          ),
          textStyle: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.2,
          ),
          elevation: 0,
        ),
      ),

      // Outlined Buttons ──────────────────────────────────────────
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: RaahatColors.textPrimary,
          minimumSize: const Size(double.infinity, 52),
          padding:
              const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          side: const BorderSide(
              color: RaahatColors.strongBorder, width: 1.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(RaahatRadius.button),
          ),
          textStyle: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.2,
          ),
        ),
      ),

      // Text Buttons ──────────────────────────────────────────────
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: RaahatColors.primaryBlue,
          minimumSize: const Size(48, 48),
          padding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          textStyle: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Cards ─────────────────────────────────────────────────────
      cardTheme: CardThemeData(
        color: RaahatColors.whiteCard,
        elevation: 0,
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 0),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.mainCard),
          side: const BorderSide(color: RaahatColors.border, width: 1),
        ),
      ),

      // Input Decoration ──────────────────────────────────────────
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: RaahatColors.whiteCard,
        contentPadding: const EdgeInsets.symmetric(
            horizontal: 16, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.input),
          borderSide: const BorderSide(color: RaahatColors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.input),
          borderSide: const BorderSide(color: RaahatColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.input),
          borderSide: const BorderSide(
              color: RaahatColors.primaryBlue, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.input),
          borderSide:
              const BorderSide(color: RaahatColors.emergencyRed),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.input),
          borderSide: const BorderSide(
              color: RaahatColors.emergencyRed, width: 2),
        ),
        labelStyle: GoogleFonts.inter(
            color: RaahatColors.textSecondary, fontSize: 14),
        hintStyle: GoogleFonts.inter(
            color: RaahatColors.textLight, fontSize: 14),
      ),

      // Typography ────────────────────────────────────────────────
      textTheme: TextTheme(
        displayLarge: GoogleFonts.barlowCondensed(
          fontSize: 52,
          fontWeight: FontWeight.w700,
          color: RaahatColors.textPrimary,
          height: 1.1,
          letterSpacing: -0.5,
        ),
        displayMedium: GoogleFonts.barlowCondensed(
          fontSize: 48,
          fontWeight: FontWeight.w700,
          color: RaahatColors.textPrimary,
          height: 1.15,
        ),
        headlineLarge: GoogleFonts.barlowCondensed(
          fontSize: 34,
          fontWeight: FontWeight.w600,
          color: RaahatColors.textPrimary,
          height: 1.2,
        ),
        headlineMedium: GoogleFonts.inter(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: RaahatColors.textPrimary,
        ),
        titleLarge: GoogleFonts.inter(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: RaahatColors.textPrimary,
          height: 1.35,
        ),
        titleMedium: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: RaahatColors.textPrimary,
        ),
        bodyLarge: GoogleFonts.inter(
          fontSize: 17,
          fontWeight: FontWeight.w400,
          color: RaahatColors.textPrimary,
          height: 1.5,
        ),
        bodyMedium: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w400,
          color: RaahatColors.textSecondary,
          height: 1.45,
        ),
        bodySmall: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: FontWeight.w400,
          color: RaahatColors.textMuted,
          height: 1.4,
        ),
        labelLarge: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w700,
          color: RaahatColors.textPrimary,
          letterSpacing: 0.5,
        ),
        labelSmall: GoogleFonts.inter(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: RaahatColors.textMuted,
          letterSpacing: 0.4,
        ),
      ),

      // Icons ─────────────────────────────────────────────────────
      iconTheme: const IconThemeData(
        color: RaahatColors.textPrimary,
        size: 24,
      ),

      // FAB ───────────────────────────────────────────────────────
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: RaahatColors.primaryBlue,
        foregroundColor: Colors.white,
        elevation: 4,
        sizeConstraints: BoxConstraints.tightFor(width: 56, height: 56),
      ),

      // SnackBar ──────────────────────────────────────────────────
      snackBarTheme: SnackBarThemeData(
        backgroundColor: RaahatColors.darkBackground,
        contentTextStyle: GoogleFonts.inter(
          color: RaahatColors.darkText,
          fontSize: 14,
          fontWeight: FontWeight.w500,
        ),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.card),
        ),
      ),

      // NavigationBar ─────────────────────────────────────────────
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: RaahatColors.whiteCard,
        surfaceTintColor: Colors.transparent,
        indicatorColor: RaahatColors.primaryBlue.withValues(alpha: 0.12),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: RaahatColors.primaryBlue,
            );
          }
          return GoogleFonts.inter(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: RaahatColors.textMuted,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return const IconThemeData(
              color: RaahatColors.primaryBlue,
              size: 24,
            );
          }
          return const IconThemeData(
            color: RaahatColors.textMuted,
            size: 24,
          );
        }),
      ),

      // Divider ───────────────────────────────────────────────────
      dividerTheme: const DividerThemeData(
        color: RaahatColors.border,
        thickness: 1,
      ),
    );
  }
}
