import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../models/models.dart';
import 'results_screen.dart';

class ProcessingScreen extends StatefulWidget {
  final String commodity;
  final double quantity;
  final String unit;
  final String originCity;
  final double originLat;
  final double originLon;
  final String vehicleType;
  final String language;

  const ProcessingScreen({
    super.key,
    required this.commodity,
    required this.quantity,
    required this.unit,
    required this.originCity,
    required this.originLat,
    required this.originLon,
    required this.vehicleType,
    required this.language,
  });

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  final ApiService _apiService = ApiService();
  StreamSubscription? _subscription;
  String _sessionId = '';

  // Subagent live statuses
  bool _marketDone = false;
  bool _logisticsDone = false;
  bool _weatherDone = false;
  bool _schemeDone = false;
  bool _engineCalculating = false;

  final List<String> _logs = [];

  @override
  void initState() {
    super.initState();
    _startStream();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }

  Future<void> _startStream() async {
    _sessionId = await _apiService.createSession(language: widget.language);
    
    _subscription = _apiService.analyzeArbitrageStream(
      sessionId: _sessionId,
      commodity: widget.commodity,
      quantity: widget.quantity,
      unit: widget.unit,
      originCity: widget.originCity,
      originLat: widget.originLat,
      originLon: widget.originLon,
      vehicleType: widget.vehicleType,
    ).listen((event) {
      final eventType = event['event'] as String? ?? '';
      final subagent = event['subagent'] as String? ?? '';
      final data = event['data'] as Map<String, dynamic>? ?? {};

      setState(() {
        if (data.containsKey('message')) {
          _logs.add('[$subagent] ${data['message']}');
        }

        if (subagent == 'Market Intel' && eventType == 'subagent.completed') {
          _marketDone = true;
        } else if (subagent == 'Logistics Intel' && eventType == 'subagent.completed') {
          _logisticsDone = true;
        } else if (subagent == 'Weather Risk' && eventType == 'subagent.completed') {
          _weatherDone = true;
        } else if (subagent == 'Scheme Policy' && eventType == 'subagent.completed') {
          _schemeDone = true;
        } else if (eventType == 'engine.calculating') {
          _engineCalculating = true;
        }
      });

      if (eventType == 'turn.completed') {
        final resData = data['result'] as Map<String, dynamic>?;
        if (resData != null) {
          final result = ArbitrageAnalysisResult.fromJson(resData);
          Future.delayed(const Duration(milliseconds: 600), () {
            if (mounted) {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                  builder: (context) => ResultsScreen(result: result),
                ),
              );
            }
          });
        }
      }
    }, onError: (err) {
      debugPrint('Stream error: $err');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close_rounded, color: Color(0xFF212121)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Analyzing Arbitrage...',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: const Color(0xFF212121),
          ),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            children: [
              const SizedBox(height: 20),
              // Scanning Animation Indicator
              Stack(
                alignment: Alignment.center,
                children: [
                  Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8F5E9).withValues(alpha: 0.5),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(
                    width: 80,
                    height: 80,
                    child: CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF2E7D32)),
                      strokeWidth: 3.5,
                    ),
                  ),
                  const Icon(
                    Icons.travel_explore_rounded,
                    color: Color(0xFF2E7D32),
                    size: 38,
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Text(
                'मंडियों का विश्लेषण जारी है...',
                style: GoogleFonts.poppins(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF212121),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 6),
              Text(
                '${widget.quantity} ${widget.unit} ${widget.commodity} from ${widget.originCity}',
                style: GoogleFonts.notoSans(
                  fontSize: 14,
                  color: const Color(0xFF616161),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // Subagent Timeline
              _buildAgentTile(
                icon: Icons.storefront_rounded,
                title: 'Market Intel (MSAMB & eNAM)',
                subtitle: 'Scraping APMC prices & arrivals via Bright Data...',
                isDone: _marketDone,
              ),
              const SizedBox(height: 12),
              _buildAgentTile(
                icon: Icons.local_gas_station_rounded,
                title: 'Logistics Intel (Live Diesel)',
                subtitle: 'Scraping fuel rates & road matrix...',
                isDone: _logisticsDone,
              ),
              const SizedBox(height: 12),
              _buildAgentTile(
                icon: Icons.thermostat_rounded,
                title: 'Weather & Spoilage (ICAR Model)',
                subtitle: 'Evaluating route temperature & decay...',
                isDone: _weatherDone,
              ),
              const SizedBox(height: 12),
              _buildAgentTile(
                icon: Icons.policy_rounded,
                title: 'Scheme Policy (PM-KISAN & TOP)',
                subtitle: 'Matching government freight subsidies...',
                isDone: _schemeDone,
              ),
              const SizedBox(height: 12),
              _buildAgentTile(
                icon: Icons.calculate_rounded,
                title: 'Deterministic Arbitrage Engine',
                subtitle: 'Computing exact Net Profit ranking...',
                isDone: _engineCalculating,
              ),

              const Spacer(),

              // Expandable Reasoning Accordion
              ExpansionTile(
                title: Text(
                  'See Agent Reasoning (${_logs.length} events)',
                  style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: const Color(0xFF616161)),
                ),
                children: [
                  Container(
                    height: 120,
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF5F5F5),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: ListView.builder(
                      itemCount: _logs.length,
                      itemBuilder: (context, idx) {
                        return Text(
                          _logs[idx],
                          style: const TextStyle(fontFamily: 'monospace', fontSize: 10, color: Color(0xFF37474F)),
                        );
                      },
                    ),
                  )
                ],
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAgentTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required bool isDone,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isDone ? const Color(0xFFE8F5E9).withValues(alpha: 0.5) : const Color(0xFFF8FAF8),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isDone ? const Color(0xFF2E7D32).withValues(alpha: 0.4) : Colors.grey.withValues(alpha: 0.15),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: isDone ? const Color(0xFF2E7D32) : Colors.grey[200],
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              size: 18,
              color: isDone ? Colors.white : Colors.grey[700],
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: GoogleFonts.poppins(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: const Color(0xFF212121),
                  ),
                ),
                Text(
                  subtitle,
                  style: GoogleFonts.notoSans(
                    fontSize: 11,
                    color: const Color(0xFF757575),
                  ),
                ),
              ],
            ),
          ),
          if (isDone)
            const Icon(Icons.check_circle_rounded, color: Color(0xFF2E7D32), size: 22)
          else
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFF57C00)),
            ),
        ],
      ),
    );
  }
}
