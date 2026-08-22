import 'package:flutter/material.dart';
import 'package:raahat/core/theme/design_tokens.dart';
import 'package:raahat/features/emergency/emergency_screen.dart';
import 'package:raahat/features/home/home_screen.dart';
import 'package:raahat/features/offline/offline_screen.dart';
import 'package:raahat/features/route/route_screen.dart';
import 'package:raahat/features/services/services_screen.dart';

/// Root navigation shell managing bottom navigation between the main screens.
class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    EmergencyScreen(),
    ServicesScreen(),
    RouteScreen(),
    OfflineScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: RaahatColors.canvasBackground,
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: RaahatColors.whiteCard,
          border: Border(
            top: BorderSide(
              color: RaahatColors.border,
              width: 1.0,
            ),
          ),
        ),
        child: NavigationBar(
          selectedIndex: _currentIndex,
          onDestinationSelected: _onItemTapped,
          elevation: 0,
          backgroundColor: RaahatColors.whiteCard,
          indicatorColor: RaahatColors.primaryBlue.withValues(alpha: 0.12),
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home_rounded, color: RaahatColors.primaryBlue),
              label: 'Home',
            ),
            NavigationDestination(
              icon: Icon(Icons.emergency_outlined),
              selectedIcon: Icon(Icons.emergency_rounded, color: RaahatColors.emergencyRed),
              label: 'Emergency',
            ),
            NavigationDestination(
              icon: Icon(Icons.location_on_outlined),
              selectedIcon: Icon(Icons.location_on_rounded, color: RaahatColors.primaryBlue),
              label: 'Services',
            ),
            NavigationDestination(
              icon: Icon(Icons.alt_route_outlined),
              selectedIcon: Icon(Icons.alt_route_rounded, color: RaahatColors.primaryBlue),
              label: 'Route',
            ),
            NavigationDestination(
              icon: Icon(Icons.cloud_off_outlined),
              selectedIcon: Icon(Icons.cloud_off_rounded, color: RaahatColors.primaryBlue),
              label: 'Offline',
            ),
          ],
        ),
      ),
    );
  }
}
