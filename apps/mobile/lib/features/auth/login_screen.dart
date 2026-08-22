import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:raahat/services/auth_service.dart';
import 'package:raahat/features/auth/signup_screen.dart';
import 'package:raahat/core/theme/design_tokens.dart';
import 'package:raahat/core/theme/raahat_widgets.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = AuthService();

  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      await _authService.signIn(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
      // AuthGate handles the redirection upon successful auth.
    } on FirebaseAuthException catch (e) {
      String message = 'An error occurred during login.';
      if (e.code == 'user-not-found') {
        message = 'No user found for that email.';
      } else if (e.code == 'wrong-password') {
        message = 'Wrong password provided.';
      } else if (e.code == 'invalid-email') {
        message = 'The email address is badly formatted.';
      } else if (e.code == 'invalid-credential') {
        message = 'Invalid email or password.';
      }
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final mediaQuery = MediaQuery.of(context);
    final isSmallScreen = mediaQuery.size.width < 380;

    return Scaffold(
      backgroundColor: RaahatColors.canvasBackground,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: EdgeInsets.symmetric(
              horizontal: isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg,
              vertical: RaahatSpacing.base,
            ),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // ── Official RAAHAT Logo ─────────────────────
                    Center(
                      child: RaahatLogo(
                        size: isSmallScreen ? 72 : 88,
                        showShadow: true,
                      ),
                    ),
                    const SizedBox(height: RaahatSpacing.base),
                    Text(
                      'RAAHAT',
                      style: RaahatTypography.displayHero(
                        fontSize: isSmallScreen ? 42 : 48,
                        color: RaahatColors.textPrimary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: RaahatSpacing.xs2),
                    Text(
                      'Emergency Assistance System',
                      style: RaahatTypography.eyebrow(
                        color: RaahatColors.textMuted,
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: RaahatSpacing.xl),

                    // ── Sign In Card ───────────────────────────────
                    Container(
                      padding: EdgeInsets.all(
                        isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg2,
                      ),
                      decoration: BoxDecoration(
                        color: RaahatColors.whiteCard,
                        borderRadius:
                            BorderRadius.circular(RaahatRadius.mainCard),
                        border: Border.all(color: RaahatColors.border),
                        boxShadow: RaahatShadows.card,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'Sign In',
                            style: theme.textTheme.titleLarge,
                          ),
                          const SizedBox(height: RaahatSpacing.xs),
                          Text(
                            'Enter your credentials to access emergency services',
                            style: RaahatTypography.bodySmall(
                              color: RaahatColors.textMuted,
                            ),
                          ),
                          const SizedBox(height: RaahatSpacing.lg),

                          // Email
                          TextFormField(
                            controller: _emailController,
                            keyboardType: TextInputType.emailAddress,
                            style: theme.textTheme.bodyLarge,
                            decoration: const InputDecoration(
                              labelText: 'Email Address',
                              prefixIcon: Icon(Icons.email_outlined),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Please enter your email';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: RaahatSpacing.base),

                          // Password
                          TextFormField(
                            controller: _passwordController,
                            obscureText: _obscurePassword,
                            style: theme.textTheme.bodyLarge,
                            decoration: InputDecoration(
                              labelText: 'Password',
                              prefixIcon: const Icon(Icons.lock_outline),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscurePassword
                                      ? Icons.visibility
                                      : Icons.visibility_off,
                                ),
                                onPressed: () {
                                  setState(() {
                                    _obscurePassword = !_obscurePassword;
                                  });
                                },
                              ),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Please enter your password';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: RaahatSpacing.xl),

                          // Sign In Button
                          _isLoading
                              ? const Center(
                                  child: CircularProgressIndicator(
                                    color: RaahatColors.primaryBlue,
                                  ),
                                )
                              : ElevatedButton(
                                  onPressed: _login,
                                  child: const Text('SIGN IN'),
                                ),
                        ],
                      ),
                    ),
                    const SizedBox(height: RaahatSpacing.lg),

                    // ── Sign Up Link ───────────────────────────────
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Flexible(
                          child: Text(
                            'Don\'t have an account?',
                            style: RaahatTypography.bodySmall(
                              color: RaahatColors.textMuted,
                            ),
                          ),
                        ),
                        TextButton(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const SignupScreen(),
                              ),
                            );
                          },
                          child: const Text('Sign Up'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
