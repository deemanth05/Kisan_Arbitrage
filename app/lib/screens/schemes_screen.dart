import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class SchemesScreen extends StatefulWidget {
  final String initialCommodity;
  final String initialState;

  const SchemesScreen({
    super.key,
    this.initialCommodity = 'Tomato',
    this.initialState = 'Maharashtra',
  });

  @override
  State<SchemesScreen> createState() => _SchemesScreenState();
}

class _SchemesScreenState extends State<SchemesScreen> {
  final ApiService _apiService = ApiService();
  late TextEditingController _commodityController;
  late String _selectedState;
  bool _isLoading = false;
  List<SchemeCardData> _schemes = [];

  final List<String> _indianStates = [
    'Maharashtra',
    'Karnataka',
    'Gujarat',
    'Madhya Pradesh',
    'Punjab',
    'Uttar Pradesh',
    'Rajasthan',
    'Tamil Nadu',
    'Andhra Pradesh',
    'Telangana',
    'Haryana',
    'West Bengal',
    'Bihar',
    'Odisha',
  ];

  @override
  void initState() {
    super.initState();
    _commodityController = TextEditingController(text: widget.initialCommodity);
    _selectedState = _indianStates.contains(widget.initialState) ? widget.initialState : 'Maharashtra';
    _discoverSchemes();
  }

  @override
  void dispose() {
    _commodityController.dispose();
    super.dispose();
  }

  Future<void> _discoverSchemes() async {
    setState(() => _isLoading = true);
    final results = await _apiService.fetchDiscoveredSchemes(
      commodity: _commodityController.text.trim(),
      state: _selectedState,
    );
    setState(() {
      _schemes = results;
      _isLoading = false;
    });
  }

  Future<void> _openPortalUrl(String url) async {
    if (url.isEmpty) return;
    try {
      final uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Portal Link: $url'),
              backgroundColor: const Color(0xFF2E7D32),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Opening: $url'),
            backgroundColor: const Color(0xFF2E7D32),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
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
          'Farmer Scheme Discovery',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: const Color(0xFF212121),
          ),
        ),
      ),
      body: Column(
        children: [
          // Filter / Search Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(bottom: BorderSide(color: Colors.grey.withValues(alpha: 0.15))),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: TextField(
                        controller: _commodityController,
                        decoration: InputDecoration(
                          labelText: 'Crop / Commodity',
                          labelStyle: GoogleFonts.poppins(fontSize: 12),
                          prefixIcon: const Icon(Icons.eco_rounded, color: Color(0xFF2E7D32), size: 20),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      flex: 3,
                      child: DropdownButtonFormField<String>(
                        value: _selectedState,
                        isExpanded: true,
                        decoration: InputDecoration(
                          labelText: 'State',
                          labelStyle: GoogleFonts.poppins(fontSize: 12),
                          prefixIcon: const Icon(Icons.location_on_rounded, color: Color(0xFF2E7D32), size: 20),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        items: _indianStates.map((s) => DropdownMenuItem(value: s, child: Text(s, style: GoogleFonts.poppins(fontSize: 12), overflow: TextOverflow.ellipsis))).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _selectedState = val);
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton.filled(
                      style: IconButton.filledStyleFrom(backgroundColor: const Color(0xFF2E7D32)),
                      icon: const Icon(Icons.search_rounded, color: Colors.white),
                      onPressed: _isLoading ? null : _discoverSchemes,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.hub_rounded, size: 14, color: Color(0xFF00796B)),
                    const SizedBox(width: 4),
                    Text(
                      'Live Discovery powered by Bright Data Search & Central Scheme Catalog',
                      style: GoogleFonts.notoSans(fontSize: 11, color: const Color(0xFF004D40), fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Body Content
          Expanded(
            child: _isLoading
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const CircularProgressIndicator(color: Color(0xFF2E7D32)),
                        const SizedBox(height: 16),
                        Text(
                          '🔍 Discovering eligible schemes for ${_commodityController.text} in $_selectedState...',
                          style: GoogleFonts.poppins(fontSize: 13, color: const Color(0xFF616161)),
                        ),
                        Text(
                          'Powered by Bright Data Web & Central Catalog',
                          style: GoogleFonts.notoSans(fontSize: 11, color: const Color(0xFF9E9E9E)),
                        ),
                      ],
                    ),
                  )
                : _schemes.isEmpty
                    ? Center(
                        child: Text(
                          'No schemes found for this query.',
                          style: GoogleFonts.poppins(fontSize: 14, color: const Color(0xFF757575)),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _schemes.length,
                        itemBuilder: (context, index) {
                          final s = _schemes[index];
                          final isLive = s.dataSource.contains('BRIGHT_DATA') || s.dataSource.contains('DISCOVERY');

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
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.all(10),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF2E7D32).withValues(alpha: 0.12),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: const Icon(Icons.policy_rounded, color: Color(0xFF2E7D32), size: 24),
                                    ),
                                    const SizedBox(width: 14),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            s.title.isNotEmpty ? s.title : s.schemeName,
                                            style: GoogleFonts.poppins(
                                              fontSize: 15,
                                              fontWeight: FontWeight.bold,
                                              color: const Color(0xFF212121),
                                            ),
                                          ),
                                          if (s.ministry != null && s.ministry!.isNotEmpty)
                                            Text(
                                              s.ministry!,
                                              style: GoogleFonts.notoSans(
                                                fontSize: 11,
                                                color: const Color(0xFF757575),
                                              ),
                                            ),
                                          const SizedBox(height: 4),
                                          Text(
                                            s.benefits,
                                            style: GoogleFonts.poppins(
                                              fontSize: 12,
                                              fontWeight: FontWeight.w600,
                                              color: const Color(0xFF2E7D32),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  s.description,
                                  style: GoogleFonts.notoSans(
                                    fontSize: 13,
                                    height: 1.4,
                                    color: const Color(0xFF616161),
                                  ),
                                ),
                                if (s.eligibilityCriteria != null && s.eligibilityCriteria!.isNotEmpty) ...[
                                  const SizedBox(height: 8),
                                  Text(
                                    'Eligibility: ${s.eligibilityCriteria}',
                                    style: GoogleFonts.notoSans(
                                      fontSize: 12,
                                      fontStyle: FontStyle.italic,
                                      color: const Color(0xFF424242),
                                    ),
                                  ),
                                ],
                                const SizedBox(height: 14),
                                Wrap(
                                  spacing: 8,
                                  runSpacing: 8,
                                  crossAxisAlignment: WrapCrossAlignment.center,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFFE8F5E9),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Text(
                                        '✅ ${s.eligibilityBadge}',
                                        style: GoogleFonts.poppins(
                                          fontSize: 11,
                                          fontWeight: FontWeight.bold,
                                          color: const Color(0xFF1B5E20),
                                        ),
                                      ),
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: isLive ? const Color(0xFFE0F2F1) : const Color(0xFFEDE7F6),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Text(
                                        isLive ? '🔴 LIVE DISCOVERED' : '🏛️ CENTRAL POLICY',
                                        style: GoogleFonts.poppins(
                                          fontSize: 10,
                                          fontWeight: FontWeight.w600,
                                          color: isLive ? const Color(0xFF004D40) : const Color(0xFF4A148C),
                                        ),
                                      ),
                                    ),
                                    const Spacer(),
                                    ElevatedButton(
                                      onPressed: () => _openPortalUrl(s.deepLink.isNotEmpty ? s.deepLink : (s.applicationUrl ?? '')),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: const Color(0xFF2E7D32),
                                        foregroundColor: Colors.white,
                                        elevation: 0,
                                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                      ),
                                      child: Text(
                                        'Open Portal →',
                                        style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
