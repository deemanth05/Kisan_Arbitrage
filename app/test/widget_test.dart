import 'package:flutter_test/flutter_test.dart';
import 'package:kisan_arbitrage/main.dart';

void main() {
  testWidgets('KisanArbitrage App initial render smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const KisanArbitrageApp());
    expect(find.text('KisanArbitrage'), findsOneWidget);
    expect(find.text('आगे बढ़ें / Get Started'), findsOneWidget);
  });
}
