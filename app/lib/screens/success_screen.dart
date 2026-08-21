import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'home_screen.dart';

class SuccessScreen extends StatelessWidget {
  final String mandiName;
  final double netProfit;
  final String commodity;
  final double quantity;
  final String transporterPhone;

  const SuccessScreen({
    super.key,
    required this.mandiName,
    required this.netProfit,
    required this.commodity,
    required this.quantity,
    required this.transporterPhone,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            children: [
              const Spacer(),
              Container(
                width: 120,
                height: 120,
                decoration: const BoxDecoration(
                  color: Color(0xFFE8F5E9),
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Icon(
                    Icons.check_circle_rounded,
                    size: 72,
                    color: Color(0xFF2E7D32),
                  ),
                ),
              ),
              const SizedBox(height: 28),
              Text(
                'Transporter Notified! 🚚',
                style: GoogleFonts.poppins(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF1B5E20),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'WhatsApp dispatch message sent to $transporterPhone',
                style: GoogleFonts.notoSans(
                  fontSize: 14,
                  color: const Color(0xFF616161),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // Dispatch Summary Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFFF9FAF9),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: Colors.grey.withValues(alpha: 0.15)),
                ),
                child: Column(
                  children: [
                    _buildDetailRow('Destination Mandi', mandiName),
                    _buildDetailRow('Produce Quantity', '$quantity Quintals $commodity'),
                    _buildDetailRow('Expected Net Profit', '₹${netProfit.toInt()}'),
                    _buildDetailRow('Estimated Pickup ETA', 'Within ~2 Hours'),
                  ],
                ),
              ),
              const Spacer(),

              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushAndRemoveUntil(
                      context,
                      MaterialPageRoute(builder: (context) => const HomeScreen()),
                      (route) => false,
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2E7D32),
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text(
                    'Back to Home / होम पर जाएं',
                    style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: GoogleFonts.notoSans(fontSize: 13, color: const Color(0xFF757575))),
          Flexible(
            child: Text(
              value,
              style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: const Color(0xFF212121)),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }
}
