import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:raahat/core/theme/design_tokens.dart';
import 'package:raahat/core/theme/raahat_widgets.dart';

/// Minimal user profile screen displaying Firebase Auth user info.
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;
    final displayName = user?.displayName ?? 'RAAHAT User';
    final email = user?.email ?? 'No email available';
    final photoUrl = user?.photoURL;

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
          'User Profile',
          style: RaahatTypography.cardTitle(
            color: RaahatColors.textPrimary,
          ),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 520),
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(
                horizontal: RaahatSpacing.lg,
                vertical: RaahatSpacing.lg,
              ),
              child: Column(
                children: [
                  // ── Avatar ──────────────────────────────────────────
                  CircleAvatar(
                    radius: 48,
                    backgroundColor: RaahatColors.primaryBlue.withValues(alpha: 0.1),
                    backgroundImage: photoUrl != null ? NetworkImage(photoUrl) : null,
                    child: photoUrl == null
                        ? const Icon(
                            Icons.person_rounded,
                            size: 48,
                            color: RaahatColors.primaryBlue,
                          )
                        : null,
                  ),
                  const SizedBox(height: RaahatSpacing.lg),

                  // ── Name ────────────────────────────────────────────
                  Text(
                    displayName,
                    style: RaahatTypography.displayH3(
                      color: RaahatColors.textPrimary,
                      fontSize: 22,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: RaahatSpacing.xs),
                  Text(
                    email,
                    style: RaahatTypography.bodySmall(
                      color: RaahatColors.textMuted,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: RaahatSpacing.xl),

                  // ── Account Info Card ───────────────────────────────
                  RaahatLightCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'ACCOUNT INFORMATION',
                          style: RaahatTypography.mono(
                            fontSize: 11,
                            color: RaahatColors.primaryBlue,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(height: RaahatSpacing.base),
                        _buildInfoRow(
                          icon: Icons.email_outlined,
                          label: 'Email',
                          value: email,
                        ),
                        const Divider(color: RaahatColors.border, height: RaahatSpacing.lg2),
                        _buildInfoRow(
                          icon: Icons.verified_user_outlined,
                          label: 'Email Verified',
                          value: (user?.emailVerified ?? false) ? 'Yes' : 'No',
                        ),
                        const Divider(color: RaahatColors.border, height: RaahatSpacing.lg2),
                        _buildInfoRow(
                          icon: Icons.calendar_today_outlined,
                          label: 'Account Created',
                          value: user?.metadata.creationTime?.toLocal().toString().split(' ').first ?? 'Unknown',
                        ),
                      ],
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

  Widget _buildInfoRow({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      children: [
        Icon(icon, size: 20, color: RaahatColors.textMuted),
        const SizedBox(width: RaahatSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: RaahatTypography.eyebrow(
                  color: RaahatColors.textMuted,
                ).copyWith(fontSize: 11),
              ),
              const SizedBox(height: RaahatSpacing.xs2),
              Text(
                value,
                style: RaahatTypography.bodyRegular(
                  color: RaahatColors.textPrimary,
                  fontWeight: FontWeight.w600,
                ).copyWith(fontSize: 14),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
