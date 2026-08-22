import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:raahat/core/config/dev_config.dart';
import 'package:raahat/core/theme/design_tokens.dart';
import 'package:raahat/core/theme/raahat_widgets.dart';
import 'package:raahat/features/home/main_navigation_shell.dart';
import 'package:raahat/features/auth/login_screen.dart';
import 'package:raahat/services/user_service.dart';
import 'package:raahat/services/api_client.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final UserService _userService = UserService(apiClient: ApiClient.instance);

  User? _currentUser;
  bool _isSyncing = false;
  String? _syncError;
  bool _syncSuccess = false;

  @override
  void initState() {
    super.initState();
    FirebaseAuth.instance.authStateChanges().listen((user) {
      if (mounted) {
        setState(() {
          _currentUser = user;
          if (user != null) {
            _syncUser();
          } else {
            _isSyncing = false;
            _syncError = null;
            _syncSuccess = false;
          }
        });
      }
    });
  }

  Future<void> _syncUser() async {
    setState(() {
      _isSyncing = true;
      _syncError = null;
      _syncSuccess = false;
    });

    // ── DEVELOPMENT BYPASS ──────────────────────────────────────────────────
    if (kDevelopmentUiBypass) {
      debugPrint(
        '[DEV] kDevelopmentUiBypass=true — skipping /users/me backend sync.',
      );
      if (mounted) {
        setState(() {
          _syncSuccess = true;
          _isSyncing = false;
        });
      }
      return;
    }
    // ── END DEVELOPMENT BYPASS ───────────────────────────────────────────────

    try {
      await _userService.getMe();
      if (mounted) {
        setState(() {
          _syncSuccess = true;
          _isSyncing = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _syncError = e.toString();
          _isSyncing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_currentUser == null) {
      return const LoginScreen();
    }

    if (_isSyncing) {
      return Scaffold(
        backgroundColor: RaahatColors.canvasBackground,
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(RaahatSpacing.lg),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const RaahatLogo(size: 72, showShadow: true),
                const SizedBox(height: RaahatSpacing.lg2),
                const CircularProgressIndicator(
                  color: RaahatColors.primaryBlue,
                ),
                const SizedBox(height: RaahatSpacing.base),
                Text(
                  'Synchronizing account...',
                  style: RaahatTypography.bodyRegular(
                    color: RaahatColors.textSecondary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    if (_syncError != null) {
      return Scaffold(
        backgroundColor: RaahatColors.canvasBackground,
        body: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(RaahatSpacing.lg),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: Container(
                padding: const EdgeInsets.all(RaahatSpacing.lg2),
                decoration: BoxDecoration(
                  color: RaahatColors.whiteCard,
                  borderRadius: BorderRadius.circular(RaahatRadius.mainCard),
                  border: Border.all(color: RaahatColors.redBorder),
                  boxShadow: RaahatShadows.card,
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(RaahatSpacing.md),
                      decoration: const BoxDecoration(
                        color: RaahatColors.redLight,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.error_outline_rounded,
                        color: RaahatColors.emergencyRed,
                        size: 40,
                      ),
                    ),
                    const SizedBox(height: RaahatSpacing.base),
                    Text(
                      'Failed to Sync Account',
                      style: RaahatTypography.cardTitle(
                        color: RaahatColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: RaahatSpacing.sm),
                    Text(
                      _syncError!,
                      textAlign: TextAlign.center,
                      style: RaahatTypography.bodySmall(
                        color: RaahatColors.emergencyRed,
                      ),
                    ),
                    const SizedBox(height: RaahatSpacing.lg2),
                    ElevatedButton.icon(
                      onPressed: _syncUser,
                      icon: const Icon(Icons.refresh),
                      label: const Text('RETRY SYNC'),
                    ),
                    const SizedBox(height: RaahatSpacing.sm),
                    TextButton(
                      onPressed: () => FirebaseAuth.instance.signOut(),
                      child: const Text('Sign Out'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    }

    if (_syncSuccess) {
      return const MainNavigationShell();
    }

    return const Scaffold(
      backgroundColor: RaahatColors.canvasBackground,
      body: Center(
        child: CircularProgressIndicator(
          color: RaahatColors.primaryBlue,
        ),
      ),
    );
  }
}
