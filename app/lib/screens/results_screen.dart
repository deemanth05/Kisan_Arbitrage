import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/models.dart';
import 'approval_gate_modal.dart';
import 'schemes_screen.dart';

class ResultsScreen extends StatelessWidget {
  final ArbitrageAnalysisResult result;

  const ResultsScreen({super.key, required this.result});

  void _openApprovalModal(BuildContext context, MandiArbitrageOption mandi) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => ApprovalGateModal(
        sessionId: result.sessionId,
        recommendedMandi: mandi,
        localBaseline: result.alternativeMandis.isNotEmpty ? result.alternativeMandis.last : null,
        commodity: result.commodity,
        quantity: result.quantity,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final allMandis = [result.recommendedMandi, ...result.alternativeMandis];

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF8),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF212121)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Arbitrage Results',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: const Color(0xFF212121),
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.volume_up_rounded, color: Color(0xFF2E7D32)),
            tooltip: 'बोलकर सुनें / Read Aloud',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(result.localizedExplanation),
                  backgroundColor: const Color(0xFF2E7D32),
                  duration: const Duration(seconds: 4),
                ),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Query Summary Chip
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(30),
              ),
              child: Row(
                children: [
                  const Icon(Icons.eco_rounded, color: Color(0xFF2E7D32), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${result.commodity} • ${result.quantity} ${result.unit} • From ${result.originCity}',
                      style: GoogleFonts.poppins(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFF1B5E20),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // "Best Time to Sell" Predictive Banner
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFE3F2FD), Color(0xFFBBDEFB)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF90CAF9).withValues(alpha: 0.5)),
              ),
              child: Row(
                children: [
                  const Text('🔮', style: TextStyle(fontSize: 28)),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          result.bestTimeToSell == 'SELL_TODAY' ? 'SELL TODAY (तुरंत बेचें)' : 'HOLD 2-3 DAYS (रुकें)',
                          style: GoogleFonts.poppins(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFF0D47A1),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          result.predictionRationale,
                          style: GoogleFonts.notoSans(
                            fontSize: 12,
                            color: const Color(0xFF1565C0),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Localized Explanation Box
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFF2E7D32).withValues(alpha: 0.2)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.psychology_rounded, color: Color(0xFF2E7D32), size: 22),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      result.localizedExplanation,
                      style: GoogleFonts.notoSans(
                        fontSize: 13,
                        height: 1.4,
                        color: const Color(0xFF212121),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            Text(
              'Mandi Profit Comparison (मंडियों की तुलना)',
              style: GoogleFonts.poppins(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF212121),
              ),
            ),
            const SizedBox(height: 12),

            // List of Mandi Profit Cards
            ...allMandis.map((mandi) => _buildMandiCard(context, mandi)),
            const SizedBox(height: 16),

            // Eligible Government Schemes Preview Card
            InkWell(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const SchemesScreen()),
                );
              },
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF2E7D32).withValues(alpha: 0.3)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: const BoxDecoration(
                        color: Color(0xFFE8F5E9),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.policy_rounded, color: Color(0xFF2E7D32), size: 24),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Government Schemes Available',
                            style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.bold, color: const Color(0xFF212121)),
                          ),
                          Text(
                            '${result.eligibleSchemes.length} schemes matched for ${result.commodity} (PM-KISAN, PMFBY, TOP)',
                            style: GoogleFonts.notoSans(fontSize: 12, color: const Color(0xFF616161)),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.arrow_forward_ios_rounded, size: 16, color: Color(0xFF2E7D32)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildMandiCard(BuildContext context, MandiArbitrageOption mandi) {
    final isRec = mandi.isRecommended;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: isRec ? const Color(0xFFF1F8F1) : Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isRec ? const Color(0xFF2E7D32) : Colors.grey.withValues(alpha: 0.2),
          width: isRec ? 2.0 : 1.0,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Ribbon
          if (isRec)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
              decoration: const BoxDecoration(
                color: Color(0xFF2E7D32),
                borderRadius: BorderRadius.vertical(top: Radius.circular(18)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.emoji_events_rounded, color: Colors.white, size: 16),
                  const SizedBox(width: 6),
                  Text(
                    '🏆 TOP RECOMMENDED MANDI (सर्वोत्तम विकल्प)',
                    style: GoogleFonts.poppins(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
            ),

          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            mandi.mandiName,
                            style: GoogleFonts.poppins(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: const Color(0xFF212121),
                            ),
                          ),
                          Text(
                            '${mandi.district}, ${mandi.state} • ${mandi.distanceKm.toInt()} km away',
                            style: GoogleFonts.notoSans(
                              fontSize: 12,
                              color: const Color(0xFF757575),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          '₹${mandi.breakdown.netProfit.toInt()}',
                          style: GoogleFonts.poppins(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFF1B5E20),
                          ),
                        ),
                        Text(
                          'Net Profit',
                          style: GoogleFonts.notoSans(
                            fontSize: 11,
                            color: const Color(0xFF757575),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Benchmark Pill Badge & Provenance
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: mandi.benchmarkStatus == 'ABOVE_BENCHMARK'
                            ? const Color(0xFFE8F5E9)
                            : const Color(0xFFFFF3E0),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        mandi.benchmarkStatus == 'ABOVE_BENCHMARK'
                            ? '✅ ₹${mandi.benchmarkDiff.toInt()} ABOVE BENCHMARK'
                            : '⚠️ ₹${mandi.benchmarkDiff.abs().toInt()} BELOW BENCHMARK',
                        style: GoogleFonts.poppins(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: mandi.benchmarkStatus == 'ABOVE_BENCHMARK'
                              ? const Color(0xFF1B5E20)
                              : const Color(0xFFE65100),
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE0F2F1),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFF80CBC4)),
                      ),
                      child: Text(
                        '📡 ${mandi.dataProvenance}',
                        style: GoogleFonts.notoSans(
                          fontSize: 10,
                          fontWeight: FontWeight.w500,
                          color: const Color(0xFF004D40),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // 7-Day Sparkline Chart
                if (mandi.sparklinePrices.isNotEmpty) ...[
                  SizedBox(
                    height: 40,
                    child: LineChart(
                      LineChartData(
                        gridData: const FlGridData(show: false),
                        titlesData: const FlTitlesData(show: false),
                        borderData: FlBorderData(show: false),
                        lineBarsData: [
                          LineChartBarData(
                            spots: mandi.sparklinePrices
                                .asMap()
                                .entries
                                .map((e) => FlSpot(e.key.toDouble(), e.value))
                                .toList(),
                            isCurved: true,
                            color: mandi.trendDirection == 'UP' ? const Color(0xFF2E7D32) : const Color(0xFFC62828),
                            barWidth: 2.5,
                            isStrokeCapRound: true,
                            dotData: const FlDotData(show: false),
                            belowBarData: BarAreaData(
                              show: true,
                              color: (mandi.trendDirection == 'UP' ? const Color(0xFF2E7D32) : const Color(0xFFC62828)).withValues(alpha: 0.12),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('7-Day Trend: ${mandi.trendDirection}', style: GoogleFonts.notoSans(fontSize: 11, color: const Color(0xFF757575))),
                      Text('Modal: ₹${mandi.modalPrice.toInt()}/q', style: GoogleFonts.poppins(fontSize: 11, fontWeight: FontWeight.bold)),
                    ],
                  ),
                ],
                const SizedBox(height: 14),

                // Detailed Cost Breakdown Accordion
                Theme(
                  data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                  child: ExpansionTile(
                    tilePadding: EdgeInsets.zero,
                    title: Text(
                      'Cost & Deductions Breakdown',
                      style: GoogleFonts.poppins(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFF2E7D32),
                      ),
                    ),
                    children: [
                      _buildCostItem('Gross Expected Value', '+₹${mandi.breakdown.grossRevenue.toInt()}', isPositive: true),
                      _buildCostItem('Freight (Live Diesel ₹${mandi.breakdown.dieselPricePerLitre.toInt()}/L)', '-₹${mandi.breakdown.freightCost.toInt()}'),
                      _buildCostItem('APMC Statutory Cess (${mandi.breakdown.apmcCessPercentage}%)', '-₹${mandi.breakdown.apmcCess.toInt()}'),
                      _buildCostItem('Hamali & Weighment', '-₹${mandi.breakdown.weighmentLoading.toInt()}'),
                      _buildCostItem('ICAR Spoilage Loss (${mandi.breakdown.spoilagePercentage}%)', '-₹${mandi.breakdown.spoilageLossAmount.toInt()}'),
                    ],
                  ),
                ),
                const SizedBox(height: 10),

                // CTA Select Button
                SizedBox(
                  width: double.infinity,
                  height: 46,
                  child: ElevatedButton(
                    onPressed: () => _openApprovalModal(context, mandi),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isRec ? const Color(0xFF2E7D32) : Colors.white,
                      foregroundColor: isRec ? Colors.white : const Color(0xFF2E7D32),
                      elevation: 0,
                      side: BorderSide(color: const Color(0xFF2E7D32), width: isRec ? 0 : 1.5),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: Text(
                      isRec ? 'Select Recommended Mandi →' : 'Select ${mandi.mandiName}',
                      style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCostItem(String label, String value, {bool isPositive = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: GoogleFonts.notoSans(fontSize: 12, color: const Color(0xFF616161))),
          Text(
            value,
            style: GoogleFonts.poppins(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isPositive ? const Color(0xFF1B5E20) : const Color(0xFFC62828),
            ),
          ),
        ],
      ),
    );
  }
}
