import 'package:flutter/material.dart';
import 'package:raahat/core/theme/design_tokens.dart';
import 'package:raahat/core/theme/raahat_widgets.dart';

/// Minimal settings screen with placeholder preference options.
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: RaahatColors.canvasBackground,
      appBar: AppBar(
        backgroundColor: RaahatColors.whiteCard,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: RaahatColors.textPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Settings',
          style: RaahatTypography.cardTitle(
            color: RaahatColors.textPrimary,
          ),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 520),
            child: ListView(
              padding: const EdgeInsets.symmetric(
                horizontal: RaahatSpacing.lg,
                vertical: RaahatSpacing.lg,
              ),
              children: [
                // ── General Section ─────────────────────────────────
                _buildSectionHeader('GENERAL'),
                const SizedBox(height: RaahatSpacing.sm2),
                RaahatLightCard(
                  padding: EdgeInsets.zero,
                  child: Column(
                    children: [
                      _buildSettingsTile(
                        icon: Icons.notifications_outlined,
                        title: 'Notifications',
                        subtitle: 'Emergency alerts & updates',
                        onTap: () => _showComingSoon(context),
                      ),
                      const Divider(color: RaahatColors.border, height: 1),
                      _buildSettingsTile(
                        icon: Icons.language_rounded,
                        title: 'Language',
                        subtitle: 'English',
                        onTap: () => _showComingSoon(context),
                      ),
                      const Divider(color: RaahatColors.border, height: 1),
                      _buildSettingsTile(
                        icon: Icons.location_on_outlined,
                        title: 'Location Services',
                        subtitle: 'Manage permissions',
                        onTap: () => _showComingSoon(context),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: RaahatSpacing.lg),

                // ── Safety Section ──────────────────────────────────
                _buildSectionHeader('SAFETY'),
                const SizedBox(height: RaahatSpacing.sm2),
                RaahatLightCard(
                  padding: EdgeInsets.zero,
                  child: Column(
                    children: [
                      _buildSettingsTile(
                        icon: Icons.contacts_outlined,
                        title: 'Emergency Contacts',
                        subtitle: 'Manage emergency contacts',
                        onTap: () => _showComingSoon(context),
                      ),
                      const Divider(color: RaahatColors.border, height: 1),
                      _buildSettingsTile(
                        icon: Icons.download_outlined,
                        title: 'Offline Packs',
                        subtitle: 'Manage downloaded data',
                        onTap: () => _showComingSoon(context),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: RaahatSpacing.lg),

                // ── About Section ───────────────────────────────────
                _buildSectionHeader('ABOUT'),
                const SizedBox(height: RaahatSpacing.sm2),
                RaahatLightCard(
                  padding: EdgeInsets.zero,
                  child: Column(
                    children: [
                      _buildSettingsTile(
                        icon: Icons.info_outline_rounded,
                        title: 'About RAAHAT',
                        subtitle: 'Version 1.0.0',
                        onTap: () => _showComingSoon(context),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: RaahatSpacing.xs),
      child: Text(
        title,
        style: RaahatTypography.mono(
          fontSize: 11,
          color: RaahatColors.textMuted,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _buildSettingsTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon, color: RaahatColors.textSecondary, size: 22),
      title: Text(
        title,
        style: RaahatTypography.bodyRegular(
          color: RaahatColors.textPrimary,
          fontWeight: FontWeight.w600,
        ).copyWith(fontSize: 14),
      ),
      subtitle: Text(
        subtitle,
        style: RaahatTypography.bodySmall(
          color: RaahatColors.textMuted,
        ).copyWith(fontSize: 12),
      ),
      trailing: const Icon(
        Icons.chevron_right_rounded,
        color: RaahatColors.textLight,
        size: 20,
      ),
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: RaahatSpacing.base,
        vertical: RaahatSpacing.xs2,
      ),
    );
  }

  void _showComingSoon(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('This setting will be available in a future update.')),
    );
  }
}
