import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import 'success_screen.dart';

class ApprovalGateModal extends StatefulWidget {
  final String sessionId;
  final MandiArbitrageOption recommendedMandi;
  final MandiArbitrageOption? localBaseline;
  final String commodity;
  final double quantity;

  const ApprovalGateModal({
    super.key,
    required this.sessionId,
    required this.recommendedMandi,
    this.localBaseline,
    required this.commodity,
    required this.quantity,
  });

  @override
  State<ApprovalGateModal> createState() => _ApprovalGateModalState();
}

class _ApprovalGateModalState extends State<ApprovalGateModal> {
  final ApiService _apiService = ApiService();
  bool _isApproving = false;
  final TextEditingController _phoneController = TextEditingController(text: '+919876543210');

  Future<void> _handleApproval() async {
    setState(() => _isApproving = true);
    await _apiService.approveTransport(
      sessionId: widget.sessionId,
      mandiId: widget.recommendedMandi.mandiId,
      phone: _phoneController.text,
    );

    if (mounted) {
      setState(() => _isApproving = false);
      Navigator.pop(context); // Close bottom sheet
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => SuccessScreen(
            mandiName: widget.recommendedMandi.mandiName,
            netProfit: widget.recommendedMandi.breakdown.netProfit,
            commodity: widget.commodity,
            quantity: widget.quantity,
            transporterPhone: _phoneController.text,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final netDiff = widget.recommendedMandi.breakdown.profitDifferenceVsLocal;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 44,
              height: 5,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'Confirm Transport Dispatch',
            style: GoogleFonts.poppins(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF212121),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'पारदर्शी तुलना एवं ट्रांसपोर्टर बुकिंग / Human Approval Gate',
            style: GoogleFonts.notoSans(
              fontSize: 12,
              color: const Color(0xFF757575),
            ),
          ),
          const SizedBox(height: 20),

          // Side-by-side comparison
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFF9FAF9),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.grey.withValues(alpha: 0.15)),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Local Mandi', style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: const Color(0xFF616161))),
                    Text('Target Mandi', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: const Color(0xFF1B5E20))),
                  ],
                ),
                const Divider(height: 20),
                _buildCompareRow('Gross Price', '₹${(widget.localBaseline?.modalPrice ?? 1700).toInt()}/q', '₹${widget.recommendedMandi.modalPrice.toInt()}/q'),
                _buildCompareRow('Freight Cost', '₹350 (Local)', '-₹${widget.recommendedMandi.breakdown.freightCost.toInt()}'),
                _buildCompareRow('APMC Cess', '-₹${(widget.localBaseline?.breakdown.apmcCess ?? 350).toInt()}', '-₹${widget.recommendedMandi.breakdown.apmcCess.toInt()}'),
                _buildCompareRow('Spoilage Loss', '₹0 (Immediate)', '-₹${widget.recommendedMandi.breakdown.spoilageLossAmount.toInt()}'),
                const Divider(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Net Take-Home', style: GoogleFonts.poppins(fontWeight: FontWeight.bold)),
                    Text(
                      '₹${widget.recommendedMandi.breakdown.netProfit.toInt()}',
                      style: GoogleFonts.poppins(
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                        color: const Color(0xFF1B5E20),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Savings callout banner
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFFE8F5E9),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.stars_rounded, color: Color(0xFF2E7D32), size: 24),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'You make ₹${netDiff.toInt()} MORE by selling at ${widget.recommendedMandi.mandiName}!',
                    style: GoogleFonts.poppins(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF1B5E20),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Transporter Alert Warning
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.notifications_active_rounded, color: Color(0xFFF57C00), size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Transporter will be alerted via WhatsApp with the pickup manifest.',
                  style: GoogleFonts.notoSans(fontSize: 12, color: const Color(0xFF616161)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Actions
          SizedBox(
            width: double.infinity,
            height: 54,
            child: ElevatedButton(
              onPressed: _isApproving ? null : _handleApproval,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2E7D32),
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              child: _isApproving
                  ? const CircularProgressIndicator(color: Colors.white)
                  : Text(
                      '✅ Approve & Notify Transporter',
                      style: GoogleFonts.poppins(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
            ),
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(
                'Cancel / पीछे जाएं',
                style: GoogleFonts.poppins(color: const Color(0xFF757575)),
              ),
            ),
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  Widget _buildCompareRow(String label, String left, String right) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: GoogleFonts.notoSans(fontSize: 12, color: const Color(0xFF757575))),
          Text(right, style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w600, color: const Color(0xFF212121))),
        ],
      ),
    );
  }
}
