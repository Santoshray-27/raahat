import 'package:flutter/material.dart';
import 'package:raahat/core/theme/design_tokens.dart';
import 'package:raahat/core/theme/raahat_widgets.dart';
import 'package:raahat/features/profile/profile_screen.dart';
import 'package:raahat/features/settings/settings_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final mediaQuery = MediaQuery.of(context);
    final isSmallScreen = mediaQuery.size.width < 380;

    return Scaffold(
      backgroundColor: RaahatColors.canvasBackground,
      appBar: AppBar(
        backgroundColor: RaahatColors.whiteCard,
        elevation: 0,
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const RaahatLogo(size: 28),
            const SizedBox(width: RaahatSpacing.sm2),
            Text(
              'RAAHAT',
              style: RaahatTypography.displayH3(
                color: RaahatColors.textPrimary,
                fontSize: 22,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_circle_outlined, color: RaahatColors.textPrimary),
            onPressed: () {
              showModalBottomSheet(
                context: context,
                backgroundColor: RaahatColors.whiteCard,
                shape: const RoundedRectangleBorder(
                  borderRadius: BorderRadius.vertical(top: Radius.circular(RaahatRadius.mainCard)),
                ),
                builder: (sheetContext) {
                  return SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: RaahatSpacing.sm2),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // ── Drag Handle ─────────────────────────
                          Container(
                            width: 36,
                            height: 4,
                            margin: const EdgeInsets.only(bottom: RaahatSpacing.sm2),
                            decoration: BoxDecoration(
                              color: RaahatColors.border,
                              borderRadius: BorderRadius.circular(2),
                            ),
                          ),
                          ListTile(
                            leading: const Icon(Icons.person_outline_rounded, color: RaahatColors.textSecondary),
                            title: Text(
                              'User Profile',
                              style: RaahatTypography.bodyRegular(
                                color: RaahatColors.textPrimary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            onTap: () {
                              Navigator.pop(sheetContext);
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const ProfileScreen(),
                                ),
                              );
                            },
                          ),
                          const Divider(color: RaahatColors.border, height: 1),
                          ListTile(
                            leading: const Icon(Icons.settings_outlined, color: RaahatColors.textSecondary),
                            title: Text(
                              'Settings',
                              style: RaahatTypography.bodyRegular(
                                color: RaahatColors.textPrimary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            onTap: () {
                              Navigator.pop(sheetContext);
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const SettingsScreen(),
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: SingleChildScrollView(
              padding: EdgeInsets.symmetric(
                horizontal: isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg,
                vertical: RaahatSpacing.base,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // ── System Status Strip ────────────────────────────────
                  const RaahatStatusStrip(
                    statusText: 'CONNECTED TO RAAHAT NETWORK',
                    isOnline: true,
                  ),
                  const SizedBox(height: RaahatSpacing.base),

                  // ── Emergency Action Card ──────────────────────────────
                  _buildEmergencyHeroCard(context, isSmallScreen),
                  const SizedBox(height: RaahatSpacing.lg),

                  // ── Quick Actions Header ───────────────────────────────
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Quick Actions',
                        style: RaahatTypography.cardTitle(
                          color: RaahatColors.textPrimary,
                        ).copyWith(fontSize: 17),
                      ),
                      const RaahatLiveBadge(label: 'READY'),
                    ],
                  ),
                  const SizedBox(height: RaahatSpacing.md),

                  // ── Quick Actions Grid ─────────────────────────────────
                  _buildQuickActionsGrid(theme, context),
                  const SizedBox(height: RaahatSpacing.lg),

                  // ── Recent Alerts / Safety Advisory ────────────────────
                  _buildRecentAlerts(theme),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmergencyHeroCard(BuildContext context, bool isSmallScreen) {
    return Container(
      decoration: BoxDecoration(
        color: RaahatColors.darkBackground,
        borderRadius: BorderRadius.circular(RaahatRadius.mainCard),
        border: Border.all(color: RaahatColors.darkBorder),
        boxShadow: RaahatShadows.prominent,
      ),
      padding: EdgeInsets.all(isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const RaahatSeverityBadge(severity: 'CRITICAL'),
              Flexible(
                child: Text(
                  'INSTANT DISPATCH',
                  style: RaahatTypography.mono(
                    fontSize: 11,
                    color: RaahatColors.darkGold,
                    fontWeight: FontWeight.w700,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: RaahatSpacing.md),
          Text(
            'Emergency Assistance',
            style: RaahatTypography.displayH3(
              color: RaahatColors.darkText,
              fontSize: isSmallScreen ? 22 : 26,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: RaahatSpacing.xs),
          Text(
            'Situation-aware AI triage and immediate local responder alerting.',
            style: RaahatTypography.bodySmall(
              color: RaahatColors.darkMuted,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: RaahatSpacing.lg),
          SizedBox(
            width: double.infinity,
            child: RaahatSosButton(
              label: 'ACTIVATE SOS ASSISTANCE',
              icon: Icons.emergency_share_rounded,
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Navigate to Emergency tab for comprehensive triage.'),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionsGrid(ThemeData theme, BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final crossAxisCount = constraints.maxWidth >= 560 ? 4 : 2;
        final aspectRatio = constraints.maxWidth < 400
            ? 1.05
            : (constraints.maxWidth >= 560 ? 1.1 : 1.18);

        return GridView.count(
          crossAxisCount: crossAxisCount,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: RaahatSpacing.md,
          mainAxisSpacing: RaahatSpacing.md,
          childAspectRatio: aspectRatio,
          children: [
            _buildActionCard(
              title: 'Find Services',
              subtitle: 'Hospitals & towing',
              icon: Icons.local_hospital_outlined,
              accentColor: RaahatColors.primaryBlue,
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Go to Services tab to browse nearby providers')),
                );
              },
            ),
            _buildActionCard(
              title: 'Safe Route',
              subtitle: 'Hazard-free path',
              icon: Icons.alt_route_outlined,
              accentColor: RaahatColors.blueAlternate,
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Go to Route tab to plan safe corridors')),
                );
              },
            ),
            _buildActionCard(
              title: 'Offline Mode',
              subtitle: 'Local AI & packs',
              icon: Icons.cloud_off_outlined,
              accentColor: RaahatColors.amber,
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Go to Offline tab to manage safety packs')),
                );
              },
            ),
            _buildActionCard(
              title: 'Emergency Contacts',
              subtitle: 'Family & Police',
              icon: Icons.shield_outlined,
              accentColor: RaahatColors.verifiedGreen,
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Emergency contacts configured')),
                );
              },
            ),
          ],
        );
      },
    );
  }

  Widget _buildActionCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color accentColor,
    required VoidCallback onTap,
  }) {
    return RaahatLightCard(
      padding: const EdgeInsets.all(RaahatSpacing.sm2),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(RaahatRadius.mainCard),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              padding: const EdgeInsets.all(RaahatSpacing.xs2 + 2),
              decoration: BoxDecoration(
                color: accentColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(RaahatRadius.button),
              ),
              child: Icon(icon, color: accentColor, size: 20),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  title,
                  style: RaahatTypography.cardTitle().copyWith(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: RaahatTypography.bodySmall(
                    color: RaahatColors.textMuted,
                  ).copyWith(fontSize: 10),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentAlerts(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                'Safety Advisories',
                style: RaahatTypography.cardTitle(
                  color: RaahatColors.textPrimary,
                ).copyWith(fontSize: 17),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(width: RaahatSpacing.xs),
            Text(
              'REGION: MP-09',
              style: RaahatTypography.mono(
                fontSize: 11,
                color: RaahatColors.textMuted,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: RaahatSpacing.sm2),
        Container(
          padding: const EdgeInsets.all(RaahatSpacing.base),
          decoration: BoxDecoration(
            color: const Color(0xFFFFFBEB),
            borderRadius: BorderRadius.circular(RaahatRadius.mainCard),
            border: Border.all(color: RaahatColors.amberWarning.withValues(alpha: 0.35)),
            boxShadow: RaahatShadows.card,
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(RaahatSpacing.sm),
                decoration: BoxDecoration(
                  color: RaahatColors.amberWarning.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.warning_amber_rounded,
                  color: RaahatColors.amberWarning,
                  size: 22,
                ),
              ),
              const SizedBox(width: RaahatSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Flexible(
                          child: Text(
                            'Monsoon Highway Advisory',
                            style: RaahatTypography.cardTitle(
                              color: const Color(0xFFB45309),
                            ).copyWith(fontSize: 14),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: RaahatSpacing.xs),
                        const RaahatSeverityBadge(severity: 'MEDIUM'),
                      ],
                    ),
                    const SizedBox(height: RaahatSpacing.xs),
                    Text(
                      'Waterlogging reported on AB Road / Bypass. Safe route guidance active in Navigation tab.',
                      style: RaahatTypography.bodySmall(
                        color: const Color(0xFF92400E),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
