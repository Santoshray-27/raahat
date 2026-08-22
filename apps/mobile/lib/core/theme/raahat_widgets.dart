import 'package:flutter/material.dart';
import 'package:raahat/core/theme/design_tokens.dart';

// ============================================================
// RAAHAT DESIGN SYSTEM — REUSABLE UI COMPONENTS
// ============================================================
// Shared widgets used across multiple screens in the app.
// Each maps directly to a component in the RAAHAT design spec
// with full responsiveness across 360dp to 1280dp+ viewports.
// ============================================================

// ─── OFFICIAL RAAHAT LOGO ────────────────────────────────────

/// Official RAAHAT Logo component preserving exact aspect ratio and colors.
class RaahatLogo extends StatelessWidget {
  final double size;
  final bool showShadow;

  const RaahatLogo({
    super.key,
    this.size = 64,
    this.showShadow = false,
  });

  @override
  Widget build(BuildContext context) {
    Widget imageWidget = Image.asset(
      'assets/images/logo.png',
      width: size,
      height: size,
      fit: BoxFit.contain,
      filterQuality: FilterQuality.high,
      errorBuilder: (context, error, stackTrace) {
        // High-fidelity vector fallback if asset is loading
        return Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: RaahatColors.primaryBlue.withValues(alpha: 0.1),
          ),
          child: Icon(
            Icons.health_and_safety_rounded,
            size: size * 0.6,
            color: RaahatColors.primaryBlue,
          ),
        );
      },
    );

    if (showShadow) {
      return Container(
        decoration: const BoxDecoration(
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: Color(0x2B1F4FD8),
              blurRadius: 16,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: imageWidget,
      );
    }

    return imageWidget;
  }
}

// ─── SOS BUTTON ─────────────────────────────────────────────

/// Gradient pill SOS button with a 2-second pulse animation.
///
/// Responsive: adapts padding on small screens and scales cleanly.
class RaahatSosButton extends StatefulWidget {
  final VoidCallback? onPressed;
  final String label;
  final IconData icon;
  final bool isLoading;

  const RaahatSosButton({
    super.key,
    required this.onPressed,
    this.label = 'SOS EMERGENCY',
    this.icon = Icons.warning_rounded,
    this.isLoading = false,
  });

  @override
  State<RaahatSosButton> createState() => _RaahatSosButtonState();
}

class _RaahatSosButtonState extends State<RaahatSosButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulseController;
  late final Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.04).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _pulseAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: widget.isLoading ? 1.0 : _pulseAnimation.value,
          child: child,
        );
      },
      child: Container(
        constraints: const BoxConstraints(minHeight: 48),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFFDC2626), Color(0xFFEF4444)],
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
          ),
          borderRadius: BorderRadius.circular(RaahatRadius.full),
          boxShadow: RaahatShadows.sosGlow,
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: widget.isLoading ? null : widget.onPressed,
            borderRadius: BorderRadius.circular(RaahatRadius.full),
            child: Padding(
              padding: const EdgeInsets.symmetric(
                vertical: 14,
                horizontal: 20,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (widget.isLoading)
                    const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: Colors.white,
                      ),
                    )
                  else
                    Icon(widget.icon, color: Colors.white, size: 22),
                  const SizedBox(width: RaahatSpacing.sm),
                  Flexible(
                    child: Text(
                      widget.label,
                      style: RaahatTypography.buttonText(
                        fontWeight: FontWeight.w700,
                        fontSize: 15,
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ─── STATUS STRIP ───────────────────────────────────────────

/// Dark status strip with pulsing green dot.
/// Responsive: text wraps cleanly with Flexible to prevent overflow on 360dp.
class RaahatStatusStrip extends StatefulWidget {
  final String statusText;
  final bool isOnline;

  const RaahatStatusStrip({
    super.key,
    this.statusText = 'SYSTEM ONLINE',
    this.isOnline = true,
  });

  @override
  State<RaahatStatusStrip> createState() => _RaahatStatusStripState();
}

class _RaahatStatusStripState extends State<RaahatStatusStrip>
    with SingleTickerProviderStateMixin {
  late final AnimationController _dotPulse;
  late final Animation<double> _dotOpacity;

  @override
  void initState() {
    super.initState();
    _dotPulse = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _dotOpacity = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _dotPulse, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _dotPulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: RaahatSpacing.base,
        vertical: RaahatSpacing.sm2,
      ),
      decoration: BoxDecoration(
        color: RaahatColors.darkSurface,
        borderRadius: BorderRadius.circular(RaahatRadius.card),
        border: Border.all(color: RaahatColors.darkBorder),
      ),
      child: Row(
        children: [
          AnimatedBuilder(
            animation: _dotOpacity,
            builder: (context, child) {
              return Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: widget.isOnline
                      ? RaahatColors.green.withValues(alpha: _dotOpacity.value)
                      : RaahatColors.textMuted,
                ),
              );
            },
          ),
          const SizedBox(width: RaahatSpacing.md),
          Expanded(
            child: Text(
              widget.statusText,
              style: RaahatTypography.mono(
                fontSize: 12,
                fontWeight: FontWeight.w400,
                color: RaahatColors.darkText,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}

// ─── LIVE BADGE ─────────────────────────────────────────────

/// Live / online indicator badge.
class RaahatLiveBadge extends StatelessWidget {
  final String label;

  const RaahatLiveBadge({super.key, this.label = 'LIVE'});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: RaahatSpacing.sm,
        vertical: RaahatSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: RaahatColors.liveBadgeBg,
        borderRadius: BorderRadius.circular(RaahatRadius.badge),
      ),
      child: Text(label, style: RaahatTypography.monoBadge()),
    );
  }
}

// ─── SEVERITY BADGE ─────────────────────────────────────────

/// Coloured severity pill: CRITICAL / HIGH / MEDIUM / LOW.
class RaahatSeverityBadge extends StatelessWidget {
  final String severity;

  const RaahatSeverityBadge({super.key, required this.severity});

  @override
  Widget build(BuildContext context) {
    final color = RaahatColors.severityColor(severity);
    final bgColor = RaahatColors.severityLightBg(severity);

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: RaahatSpacing.sm2,
        vertical: RaahatSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(RaahatRadius.badge),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(
        severity.toUpperCase(),
        style: RaahatTypography.eyebrow(color: color).copyWith(
          fontSize: 11,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.4,
        ),
      ),
    );
  }
}

// ─── CATEGORY CHIP ──────────────────────────────────────────

/// Filter / category chip with comfortable >= 44dp hit area.
class RaahatCategoryChip extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback? onTap;

  const RaahatCategoryChip({
    super.key,
    required this.label,
    this.isSelected = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      curve: Curves.easeInOut,
      child: Material(
        color: isSelected ? RaahatColors.primaryBlue : RaahatColors.whiteCard,
        borderRadius: BorderRadius.circular(RaahatRadius.full),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(RaahatRadius.full),
          child: Container(
            constraints: const BoxConstraints(minHeight: 36),
            padding: const EdgeInsets.symmetric(
              horizontal: RaahatSpacing.base,
              vertical: RaahatSpacing.sm,
            ),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(RaahatRadius.full),
              border: Border.all(
                color: isSelected ? RaahatColors.primaryBlue : RaahatColors.border,
              ),
            ),
            child: Text(
              label,
              style: RaahatTypography.bodySmall(
                color: isSelected ? Colors.white : RaahatColors.textSecondary,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
              ).copyWith(fontSize: 13),
            ),
          ),
        ),
      ),
    );
  }
}

// ─── LIGHT CARD ─────────────────────────────────────────────

/// Standard white card with responsive padding.
class RaahatLightCard extends StatelessWidget {
  final Widget child;
  final Color? borderColor;
  final double radius;
  final EdgeInsetsGeometry padding;

  const RaahatLightCard({
    super.key,
    required this.child,
    this.borderColor,
    this.radius = RaahatRadius.mainCard,
    this.padding = const EdgeInsets.all(RaahatSpacing.base),
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: RaahatColors.whiteCard,
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: borderColor ?? RaahatColors.border),
        boxShadow: RaahatShadows.card,
      ),
      child: child,
    );
  }
}

// ─── CONSOLE (DARK) CARD ────────────────────────────────────

/// Dark console surface card with responsive padding.
class RaahatConsoleCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;

  const RaahatConsoleCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(RaahatSpacing.lg),
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: RaahatColors.darkBackground,
        borderRadius: BorderRadius.circular(RaahatRadius.card),
        border: Border.all(color: RaahatColors.darkBorder),
      ),
      child: child,
    );
  }
}

// ─── CONSOLE INPUT ──────────────────────────────────────────

/// Dark-themed text input for console surfaces.
class RaahatConsoleInput extends StatelessWidget {
  final TextEditingController? controller;
  final String? hintText;
  final int maxLines;
  final bool enabled;
  final String? errorText;

  const RaahatConsoleInput({
    super.key,
    this.controller,
    this.hintText,
    this.maxLines = 4,
    this.enabled = true,
    this.errorText,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      maxLines: maxLines,
      enabled: enabled,
      style: RaahatTypography.mono(
        fontSize: 14,
        color: RaahatColors.darkText,
      ),
      cursorColor: RaahatColors.darkGold,
      decoration: InputDecoration(
        filled: true,
        fillColor: RaahatColors.darkBackground,
        hintText: hintText,
        hintStyle: RaahatTypography.mono(
          fontSize: 14,
          color: RaahatColors.darkMuted,
        ),
        errorText: errorText,
        errorStyle: RaahatTypography.bodySmall(color: RaahatColors.emergencyRed)
            .copyWith(fontSize: 12),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: RaahatSpacing.base,
          vertical: RaahatSpacing.md2,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.button),
          borderSide: const BorderSide(color: RaahatColors.darkBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.button),
          borderSide: const BorderSide(color: RaahatColors.darkBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.button),
          borderSide: const BorderSide(color: RaahatColors.darkGold, width: 1.5),
        ),
        disabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.button),
          borderSide: BorderSide(
              color: RaahatColors.darkBorder.withValues(alpha: 0.5)),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(RaahatRadius.button),
          borderSide: const BorderSide(color: RaahatColors.emergencyRed),
        ),
      ),
    );
  }
}
