import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:raahat/core/theme/app_theme.dart';
import 'package:raahat/core/theme/raahat_widgets.dart';
import 'package:raahat/features/home/home_screen.dart';
import 'package:raahat/features/route/route_screen.dart';
import 'package:raahat/features/offline/offline_screen.dart';

void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  const List<Size> testSizes = [
    Size(360, 640),   // Small phone (360dp)
    Size(390, 844),   // Standard phone (390dp)
    Size(480, 800),   // Wide phone (480dp)
    Size(768, 1024),  // Tablet portrait (768dp)
    Size(1024, 768),  // Tablet landscape (1024dp)
    Size(1280, 800),  // Desktop / Large screen (1280dp)
  ];

  group('RAAHAT Official Logo Verification', () {
    testWidgets('Official RaahatLogo renders with correct proportions and assets', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Center(
              child: RaahatLogo(size: 80, showShadow: true),
            ),
          ),
        ),
      );
      await tester.pump(const Duration(milliseconds: 50));

      expect(find.byType(RaahatLogo), findsOneWidget);
      expect(find.byType(Image), findsOneWidget);
    });
  });

  group('RAAHAT Responsive UI Layout Verification', () {
    for (final size in testSizes) {
      testWidgets('HomeScreen renders responsive layout at ${size.width}x${size.height}', (WidgetTester tester) async {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.lightTheme,
            home: const HomeScreen(),
          ),
        );
        await tester.pump(const Duration(milliseconds: 50));

        expect(find.text('RAAHAT'), findsOneWidget);
        expect(find.text('Emergency Assistance'), findsOneWidget);
        expect(find.text('Quick Actions'), findsOneWidget);
        expect(find.byType(RaahatLogo), findsOneWidget);
        expect(find.byType(RaahatStatusStrip), findsOneWidget);
        expect(find.byType(RaahatSosButton), findsOneWidget);
      });

      testWidgets('RouteScreen renders responsive layout at ${size.width}x${size.height}', (WidgetTester tester) async {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.lightTheme,
            home: const RouteScreen(),
          ),
        );
        await tester.pump(const Duration(milliseconds: 50));

        expect(find.text('Safe Route Planner'), findsOneWidget);
        expect(find.text('Corridor Selection'), findsOneWidget);
      });

      testWidgets('OfflineScreen renders responsive layout at ${size.width}x${size.height}', (WidgetTester tester) async {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.lightTheme,
            home: const OfflineScreen(),
          ),
        );
        await tester.pump(const Duration(milliseconds: 50));

        expect(find.text('Offline Safety Engine'), findsOneWidget);
        expect(find.text('Local AI & Telemetry Board'), findsOneWidget);
      });
    }
  });

  group('RAAHAT Reusable Components Responsiveness', () {
    testWidgets('RaahatStatusStrip wraps text without overflow on narrow 320dp width', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(320, 600);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Padding(
              padding: EdgeInsets.all(8.0),
              child: RaahatStatusStrip(
                statusText: 'CONNECTED TO RAAHAT NETWORK — REGIONAL CLUSTER ONLINE',
              ),
            ),
          ),
        ),
      );
      await tester.pump(const Duration(milliseconds: 50));

      expect(find.byType(RaahatStatusStrip), findsOneWidget);
    });

    testWidgets('RaahatSosButton renders and scales properly', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: RaahatSosButton(
                onPressed: () {},
                label: 'ACTIVATE SOS ASSISTANCE',
              ),
            ),
          ),
        ),
      );
      await tester.pump(const Duration(milliseconds: 50));

      expect(find.byType(RaahatSosButton), findsOneWidget);
      expect(find.text('ACTIVATE SOS ASSISTANCE'), findsOneWidget);
    });
  });
}
