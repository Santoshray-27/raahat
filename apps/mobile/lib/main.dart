import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';

import 'package:raahat/core/theme/app_theme.dart';
import 'package:raahat/features/auth/auth_gate.dart';
import 'firebase_options.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  runApp(const RaahatApp());
}

class RaahatApp extends StatelessWidget {
  const RaahatApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RAAHAT',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const AuthGate(),
    );
  }
}

