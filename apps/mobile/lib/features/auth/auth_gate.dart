import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
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
      return const Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Synchronizing account...'),
            ],
          ),
        ),
      );
    }

    if (_syncError != null) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, color: Colors.red, size: 48),
                const SizedBox(height: 16),
                const Text('Failed to sync account with server.'),
                const SizedBox(height: 8),
                Text(
                  _syncError!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.red),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: _syncUser,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry'),
                ),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => FirebaseAuth.instance.signOut(),
                  child: const Text('Sign Out'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    if (_syncSuccess) {
      return const MainNavigationShell();
    }

    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
