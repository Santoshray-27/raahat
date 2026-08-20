import 'package:flutter/material.dart';
import 'package:raahat/core/theme/app_theme.dart';
import 'package:raahat/features/home/main_navigation_shell.dart';

void main() {
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
      home: const MainNavigationShell(),
    );
  }
}

