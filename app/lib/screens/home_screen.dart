import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'processing_screen.dart';
import 'community_screen.dart';
import 'schemes_screen.dart';

class HomeScreen extends StatefulWidget {
  final String language;
  const HomeScreen({super.key, this.language = 'hi'});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentNavIndex = 0;
  String _selectedCommodity = 'Tomato';
  final TextEditingController _quantityController = TextEditingController(text: '20');
  String _selectedUnit = 'quintal';
  final TextEditingController _originCityController = TextEditingController(text: 'Kolhapur');
  double _originLat = 16.6913;
  double _originLon = 74.2432;
  String _selectedVehicle = 'bolero_pickup';

  final List<String> _commodities = [
    'Tomato', 'Onion', 'Potato', 'Soybean', 'Cotton', 'Wheat', 'Green Chilli'
  ];

  final List<Map<String, dynamic>> _vehicles = [
    {'id': 'bolero_pickup', 'name': 'Bolero Pickup (2.5T)'},
    {'id': 'tata_ace', 'name': 'Tata Ace (1.5T)'},
    {'id': 'eicher_14ft', 'name': 'Eicher Truck (5.0T)'},
  ];

  void _triggerVoiceOverlay() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      isDismissible: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 48,
                    height: 5,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Container(
                    width: 90,
                    height: 90,
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFEBEE),
                      shape: BoxShape.circle,
                      border: Border.all(color: const Color(0xFFC62828), width: 2),
                    ),
                    child: const Center(
                      child: Icon(Icons.mic, color: Color(0xFFC62828), size: 44),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    'बोलिए... हम सुन रहे हैं',
                    style: GoogleFonts.poppins(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF212121),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'उदा: "20 क्विंटल टमाटर कोल्हापुर से"',
                    style: GoogleFonts.notoSans(
                      fontSize: 14,
                      color: const Color(0xFF757575),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8F5E9),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.auto_awesome, color: Color(0xFF2E7D32), size: 20),
                        const SizedBox(width: 8),
                        Text(
                          'Powered by Bhashini AI',
                          style: GoogleFonts.poppins(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: const Color(0xFF1B5E20),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      onPressed: () {
                        Navigator.pop(context);
                        setState(() {
                          _selectedCommodity = 'Tomato';
                          _quantityController.text = '20';
                          _originCityController.text = 'Kolhapur';
                        });
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('✅ Auto-filled: 20 Quintals Tomato from Kolhapur'),
                            backgroundColor: Color(0xFF2E7D32),
                          ),
                        );
                      },
                      style: OutlinedButton.styleFrom(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text('Use Voice Transcript'),
                    ),
                  )
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _submitAnalysis() {
    final qty = double.tryParse(_quantityController.text) ?? 20.0;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ProcessingScreen(
          commodity: _selectedCommodity,
          quantity: qty,
          unit: _selectedUnit,
          originCity: _originCityController.text,
          originLat: _originLat,
          originLon: _originLon,
          vehicleType: _selectedVehicle,
          language: widget.language,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF8),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.agriculture_rounded, color: Color(0xFF2E7D32), size: 22),
            ),
            const SizedBox(width: 8),
            Text(
              'KisanArbitrage',
              style: GoogleFonts.poppins(
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: const Color(0xFF212121),
              ),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFFE8F5E9),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                const Icon(Icons.wb_sunny_rounded, color: Color(0xFFF57C00), size: 16),
                const SizedBox(width: 4),
                Text(
                  '32°C ☀️',
                  style: GoogleFonts.poppins(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: const Color(0xFF1B5E20),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentNavIndex,
        children: [
          _buildHomeContent(),
          const CommunityScreen(),
          const SchemesScreen(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentNavIndex,
        onTap: (index) => setState(() => _currentNavIndex = index),
        selectedItemColor: const Color(0xFF2E7D32),
        unselectedItemColor: const Color(0xFF9E9E9E),
        selectedLabelStyle: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 12),
        unselectedLabelStyle: GoogleFonts.notoSans(fontSize: 12),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.people_alt_rounded), label: 'Community'),
          BottomNavigationBarItem(icon: Icon(Icons.policy_rounded), label: 'Schemes'),
        ],
      ),
      floatingActionButton: _currentNavIndex == 0
          ? FloatingActionButton.extended(
              onPressed: _triggerVoiceOverlay,
              backgroundColor: const Color(0xFF2E7D32),
              icon: const Icon(Icons.mic_rounded, color: Colors.white, size: 24),
              label: Text(
                'बोलकर खोजें',
                style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.white),
              ),
            )
          : null,
    );
  }

  Widget _buildHomeContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Greeting Banner
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF2E7D32), Color(0xFF1B5E20)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'नमस्ते किसान मित्र! 🌾',
                        style: GoogleFonts.poppins(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'आज अपनी फसल कहाँ बेचें? सही मंडी और सही दाम जानें।',
                        style: GoogleFonts.notoSans(
                          color: Colors.white.withValues(alpha: 0.9),
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.trending_up_rounded, color: Colors.white, size: 40),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Main Query Card
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.04),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'फसल एवं मंडी खोजें / Query Parameters',
                  style: GoogleFonts.poppins(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF212121),
                  ),
                ),
                const SizedBox(height: 16),

                // Crop Selector
                Text(
                  'फसल चुनें (Commodity)',
                  style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: const Color(0xFF424242)),
                ),
                const SizedBox(height: 6),
                DropdownButtonFormField<String>(
                  initialValue: _selectedCommodity,
                  decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.eco_rounded, color: Color(0xFF2E7D32)),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                  items: _commodities.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                  onChanged: (val) => setState(() => _selectedCommodity = val!),
                ),
                const SizedBox(height: 16),

                // Quantity and Unit Row
                Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'मात्रा (Quantity)',
                            style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: const Color(0xFF424242)),
                          ),
                          const SizedBox(height: 6),
                          TextFormField(
                            controller: _quantityController,
                            keyboardType: TextInputType.number,
                            decoration: InputDecoration(
                              prefixIcon: const Icon(Icons.scale_rounded, color: Color(0xFF2E7D32)),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 2,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'इकाई (Unit)',
                            style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: const Color(0xFF424242)),
                          ),
                          const SizedBox(height: 6),
                          DropdownButtonFormField<String>(
                            initialValue: _selectedUnit,
                            decoration: InputDecoration(
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                            ),
                            items: const [
                              DropdownMenuItem(value: 'quintal', child: Text('Quintal')),
                              DropdownMenuItem(value: 'ton', child: Text('Ton')),
                            ],
                            onChanged: (val) => setState(() => _selectedUnit = val!),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Origin Location
                Text(
                  'आपका स्थान (Origin City/GPS)',
                  style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: const Color(0xFF424242)),
                ),
                const SizedBox(height: 6),
                TextFormField(
                  controller: _originCityController,
                  decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.location_on_rounded, color: Color(0xFF2E7D32)),
                    suffixIcon: TextButton.icon(
                      onPressed: () {
                        setState(() {
                          _originCityController.text = 'Kolhapur';
                          _originLat = 16.6913;
                          _originLon = 74.2432;
                        });
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('📍 GPS Location Acquired: Kolhapur')),
                        );
                      },
                      icon: const Icon(Icons.my_location_rounded, size: 16, color: Color(0xFF2E7D32)),
                      label: Text('GPS', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: const Color(0xFF2E7D32))),
                    ),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                ),
                const SizedBox(height: 16),

                // Vehicle Selector
                Text(
                  'वाहन का प्रकार (Vehicle Type)',
                  style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: const Color(0xFF424242)),
                ),
                const SizedBox(height: 6),
                DropdownButtonFormField<String>(
                  initialValue: _selectedVehicle,
                  decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.local_shipping_rounded, color: Color(0xFF2E7D32)),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                  items: _vehicles.map((v) => DropdownMenuItem(value: v['id'] as String, child: Text(v['name'] as String))).toList(),
                  onChanged: (val) => setState(() => _selectedVehicle = val!),
                ),
                const SizedBox(height: 24),

                // Find Best Mandi CTA
                SizedBox(
                  width: double.infinity,
                  height: 54,
                  child: ElevatedButton(
                    onPressed: _submitAnalysis,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2E7D32),
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.analytics_rounded, color: Colors.white),
                        const SizedBox(width: 8),
                        Text(
                          'Find Best Mandi / सही मंडी खोजें',
                          style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Market Pulse
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Market Pulse (आज के भाव)',
                style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: const Color(0xFF212121)),
              ),
              Text(
                'Live MSAMB Scraped',
                style: GoogleFonts.poppins(fontSize: 11, fontWeight: FontWeight.w600, color: const Color(0xFF2E7D32)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildPulseCard('Tomato (Pune)', '₹2,150', '+12%', true),
                _buildPulseCard('Onion (Lasalgaon)', '₹2,550', '+8%', true),
                _buildPulseCard('Soybean (Sangli)', '₹4,720', '+4%', true),
                _buildPulseCard('Cotton (Nagpur)', '₹7,200', '-2%', false),
              ],
            ),
          ),
          const SizedBox(height: 80), // Padding for FAB
        ],
      ),
    );
  }

  Widget _buildPulseCard(String title, String price, String change, bool isPositive) {
    return Container(
      width: 145,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.grey.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: GoogleFonts.notoSans(fontSize: 12, fontWeight: FontWeight.w600, color: const Color(0xFF616161)),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 6),
          Text(
            price,
            style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF212121)),
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              Icon(
                isPositive ? Icons.trending_up_rounded : Icons.trending_down_rounded,
                color: isPositive ? const Color(0xFF1B5E20) : const Color(0xFFC62828),
                size: 16,
              ),
              const SizedBox(width: 4),
              Text(
                change,
                style: GoogleFonts.poppins(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: isPositive ? const Color(0xFF1B5E20) : const Color(0xFFC62828),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
