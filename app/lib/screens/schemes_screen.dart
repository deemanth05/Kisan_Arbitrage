import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class SchemesScreen extends StatelessWidget {
  const SchemesScreen({super.key});

  final List<Map<String, dynamic>> _schemes = const [
    {
      'name': 'PM-KISAN',
      'title': 'PM Kisan Samman Nidhi',
      'desc': 'Direct income support of ₹6,000 per year transferred in 3 equal installments to all landholding farmer families.',
      'benefit': '₹6,000 / Year DBT',
      'badge': 'Active Direct Benefit',
      'icon': Icons.account_balance_rounded,
      'color': Color(0xFF2E7D32),
    },
    {
      'name': 'PMFBY (Crop Insurance)',
      'title': 'Pradhan Mantri Fasal Bima Yojana',
      'desc': 'Comprehensive risk insurance against natural calamities, unseasonal rainfall, and post-harvest localized hazards.',
      'benefit': '95% Government Premium Subsidy',
      'badge': 'Recommended for Perishables',
      'icon': Icons.shield_rounded,
      'color': Color(0xFF1565C0),
    },
    {
      'name': 'Operation Greens (TOP)',
      'title': 'MoFPI Operation Greens Transport Subsidy',
      'desc': '50% subsidy on transportation and cold storage evacuation of Tomato, Onion, and Potato crops from production clusters.',
      'benefit': '50% Freight Cost Subsidy',
      'badge': 'Active Freight Subsidy',
      'icon': Icons.local_shipping_rounded,
      'color': Color(0xFFE65100),
    },
    {
      'name': 'eNAM Direct Trade',
      'title': 'National Agriculture Market (eNAM)',
      'desc': 'Pan-India electronic trading portal uniting APMC mandis to facilitate online bidding and avoid double market cess.',
      'benefit': 'Zero Double Cess & Pan-India Bidding',
      'badge': 'Online Direct Trade',
      'icon': Icons.hub_rounded,
      'color': Color(0xFF6A1B9A),
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF8),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Text(
          'Government Schemes & Subsidies',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.bold,
            fontSize: 17,
            color: const Color(0xFF212121),
          ),
        ),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _schemes.length,
        itemBuilder: (context, index) {
          final s = _schemes[index];
          final Color themeColor = s['color'] as Color;

          return Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: Colors.grey.withValues(alpha: 0.15)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.02),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: themeColor.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(s['icon'] as IconData, color: themeColor, size: 24),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            s['title'] as String,
                            style: GoogleFonts.poppins(
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                              color: const Color(0xFF212121),
                            ),
                          ),
                          Text(
                            s['benefit'] as String,
                            style: GoogleFonts.poppins(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: themeColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  s['desc'] as String,
                  style: GoogleFonts.notoSans(
                    fontSize: 13,
                    height: 1.4,
                    color: const Color(0xFF616161),
                  ),
                ),
                const SizedBox(height: 14),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE8F5E9),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        '✅ ${s['badge']}',
                        style: GoogleFonts.poppins(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF1B5E20),
                        ),
                      ),
                    ),
                    TextButton(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Opening official portal for ${s['name']}...'),
                            backgroundColor: const Color(0xFF2E7D32),
                          ),
                        );
                      },
                      child: Text(
                        'Learn More →',
                        style: GoogleFonts.poppins(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF2E7D32),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
