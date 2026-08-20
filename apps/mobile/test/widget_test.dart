import 'package:flutter_test/flutter_test.dart';
import 'package:raahat/main.dart';

void main() {
  testWidgets('RAAHAT App launches and displays placeholder screen', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const RaahatApp());

    // Verify that RAAHAT title is rendered.
    expect(find.text('RAAHAT Emergency Assistance'), findsOneWidget);
  });
}
