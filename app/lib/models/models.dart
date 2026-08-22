class MandiCostBreakdown {
  final double grossRevenue;
  final double freightCost;
  final double dieselPricePerLitre;
  final double distanceKm;
  final double transitDurationHours;
  final double apmcCess;
  final double apmcCessPercentage;
  final double weighmentLoading;
  final double spoilageLossAmount;
  final double spoilagePercentage;
  final double transitTemperature;
  final bool hasRain;
  final double netProfit;
  final double profitDifferenceVsLocal;
  final String routingSource;
  final String weatherSource;

  MandiCostBreakdown({
    required this.grossRevenue,
    required this.freightCost,
    required this.dieselPricePerLitre,
    required this.distanceKm,
    required this.transitDurationHours,
    required this.apmcCess,
    required this.apmcCessPercentage,
    required this.weighmentLoading,
    required this.spoilageLossAmount,
    required this.spoilagePercentage,
    required this.transitTemperature,
    required this.hasRain,
    required this.netProfit,
    required this.profitDifferenceVsLocal,
    this.routingSource = "OSRM_ROAD_ROUTING",
    this.weatherSource = "OPEN_METEO_LIVE",
  });

  factory MandiCostBreakdown.fromJson(Map<String, dynamic> json) {
    return MandiCostBreakdown(
      grossRevenue: (json['gross_revenue'] as num?)?.toDouble() ?? 0.0,
      freightCost: (json['freight_cost'] as num?)?.toDouble() ?? 0.0,
      dieselPricePerLitre: (json['diesel_price_per_litre'] as num?)?.toDouble() ?? 0.0,
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0.0,
      transitDurationHours: (json['transit_duration_hours'] as num?)?.toDouble() ?? 0.0,
      apmcCess: (json['apmc_cess'] as num?)?.toDouble() ?? 0.0,
      apmcCessPercentage: (json['apmc_cess_percentage'] as num?)?.toDouble() ?? 1.05,
      weighmentLoading: (json['weighment_loading'] as num?)?.toDouble() ?? 0.0,
      spoilageLossAmount: (json['spoilage_loss_amount'] as num?)?.toDouble() ?? 0.0,
      spoilagePercentage: (json['spoilage_percentage'] as num?)?.toDouble() ?? 0.0,
      transitTemperature: (json['transit_temperature'] as num?)?.toDouble() ?? 32.0,
      hasRain: json['has_rain'] as bool? ?? false,
      netProfit: (json['net_profit'] as num?)?.toDouble() ?? 0.0,
      profitDifferenceVsLocal: (json['profit_difference_vs_local'] as num?)?.toDouble() ?? 0.0,
      routingSource: json['routing_source'] as String? ?? "OSRM_ROAD_ROUTING",
      weatherSource: json['weather_source'] as String? ?? "OPEN_METEO_LIVE",
    );
  }
}

class MandiArbitrageOption {
  final String mandiId;
  final String mandiName;
  final String district;
  final String state;
  final double lat;
  final double lon;
  final double distanceKm;
  final double modalPrice;
  final double minPrice;
  final double maxPrice;
  final String priceUnit;
  final bool isRecommended;
  final bool isLocalBaseline;
  final String benchmarkStatus;
  final String benchmarkName;
  final double benchmarkDiff;
  final String marketPulse;
  final double arrivalQuantity;
  final String arrivalUnit;
  final String arrivalDate;
  final String trendDirection;
  final List<double> sparklinePrices;
  final double? communityReportedPrice;
  final String? communityReportTime;
  final String dataSource;
  final String dataProvenance;
  final bool isLiveData;
  final bool dataAvailable;
  final MandiCostBreakdown breakdown;

  MandiArbitrageOption({
    required this.mandiId,
    required this.mandiName,
    required this.district,
    required this.state,
    required this.lat,
    required this.lon,
    required this.distanceKm,
    required this.modalPrice,
    required this.minPrice,
    required this.maxPrice,
    required this.priceUnit,
    required this.isRecommended,
    required this.isLocalBaseline,
    required this.benchmarkStatus,
    required this.benchmarkName,
    required this.benchmarkDiff,
    required this.marketPulse,
    required this.arrivalQuantity,
    required this.arrivalUnit,
    this.arrivalDate = "",
    required this.trendDirection,
    required this.sparklinePrices,
    this.communityReportedPrice,
    this.communityReportTime,
    this.dataSource = "DATA_GOV_IN_API",
    this.dataProvenance = "Official Agmarknet",
    this.isLiveData = true,
    this.dataAvailable = true,
    required this.breakdown,
  });

  factory MandiArbitrageOption.fromJson(Map<String, dynamic> json) {
    var rawSpark = json['sparkline_prices'] as List<dynamic>? ?? [];
    List<double> spark = rawSpark.map((e) => (e as num).toDouble()).toList();

    return MandiArbitrageOption(
      mandiId: json['mandi_id'] as String? ?? '',
      mandiName: json['mandi_name'] as String? ?? '',
      district: json['district'] as String? ?? '',
      state: json['state'] as String? ?? 'Maharashtra',
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lon: (json['lon'] as num?)?.toDouble() ?? 0.0,
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0.0,
      modalPrice: (json['modal_price'] as num?)?.toDouble() ?? 0.0,
      minPrice: (json['min_price'] as num?)?.toDouble() ?? 0.0,
      maxPrice: (json['max_price'] as num?)?.toDouble() ?? 0.0,
      priceUnit: json['price_unit'] as String? ?? '₹/quintal',
      isRecommended: json['is_recommended'] as bool? ?? false,
      isLocalBaseline: json['is_local_baseline'] as bool? ?? false,
      benchmarkStatus: json['benchmark_status'] as String? ?? 'ABOVE_BENCHMARK',
      benchmarkName: json['benchmark_name'] as String? ?? 'TOP Benchmark',
      benchmarkDiff: (json['benchmark_diff'] as num?)?.toDouble() ?? 0.0,
      marketPulse: json['market_pulse'] as String? ?? 'NORMAL_SUPPLY',
      arrivalQuantity: (json['arrival_quantity'] as num?)?.toDouble() ?? 0.0,
      arrivalUnit: json['arrival_unit'] as String? ?? 'Tonnes',
      arrivalDate: json['arrival_date'] as String? ?? '',
      trendDirection: json['trend_direction'] as String? ?? 'UP',
      sparklinePrices: spark,
      communityReportedPrice: (json['community_reported_price'] as num?)?.toDouble(),
      communityReportTime: json['community_report_time'] as String?,
      dataSource: json['data_source'] as String? ?? 'DATA_GOV_IN_API',
      dataProvenance: json['data_provenance'] as String? ?? 'Official Agmarknet',
      isLiveData: json['is_live_data'] as bool? ?? true,
      dataAvailable: json['data_available'] as bool? ?? true,
      breakdown: MandiCostBreakdown.fromJson(json['breakdown'] as Map<String, dynamic>? ?? {}),
    );
  }
}

class SchemeCardData {
  final String schemeName;
  final String schemeCode;
  final String title;
  final String? ministry;
  final String description;
  final String benefits;
  final String eligibilityBadge;
  final String? eligibilityCriteria;
  final List<String> documentsRequired;
  final String? applicationUrl;
  final String deepLink;
  final bool isEligible;
  final String dataSource;

  SchemeCardData({
    required this.schemeName,
    required this.schemeCode,
    required this.title,
    this.ministry,
    required this.description,
    required this.benefits,
    required this.eligibilityBadge,
    this.eligibilityCriteria,
    this.documentsRequired = const [],
    this.applicationUrl,
    required this.deepLink,
    required this.isEligible,
    this.dataSource = "CENTRAL_POLICY_CATALOG",
  });

  factory SchemeCardData.fromJson(Map<String, dynamic> json) {
    var rawDocs = json['documents_required'] as List<dynamic>? ?? [];
    List<String> docs = rawDocs.map((e) => e.toString()).toList();

    return SchemeCardData(
      schemeName: json['scheme_name'] as String? ?? '',
      schemeCode: json['scheme_code'] as String? ?? '',
      title: json['title'] as String? ?? '',
      ministry: json['ministry'] as String?,
      description: json['description'] as String? ?? '',
      benefits: json['benefits'] as String? ?? '',
      eligibilityBadge: json['eligibility_badge'] as String? ?? 'Eligible',
      eligibilityCriteria: json['eligibility_criteria'] as String?,
      documentsRequired: docs,
      applicationUrl: json['application_url'] as String?,
      deepLink: json['deep_link'] as String? ?? '',
      isEligible: json['is_eligible'] as bool? ?? true,
      dataSource: json['data_source'] as String? ?? 'CENTRAL_POLICY_CATALOG',
    );
  }
}

class ArbitrageAnalysisResult {
  final String sessionId;
  final String commodity;
  final double quantity;
  final String unit;
  final String originCity;
  final double originLat;
  final double originLon;
  final String vehicleType;
  final MandiArbitrageOption recommendedMandi;
  final List<MandiArbitrageOption> alternativeMandis;
  final String bestTimeToSell;
  final String predictionRationale;
  final String localizedExplanation;
  final List<SchemeCardData> eligibleSchemes;

  ArbitrageAnalysisResult({
    required this.sessionId,
    required this.commodity,
    required this.quantity,
    required this.unit,
    required this.originCity,
    required this.originLat,
    required this.originLon,
    required this.vehicleType,
    required this.recommendedMandi,
    required this.alternativeMandis,
    required this.bestTimeToSell,
    required this.predictionRationale,
    required this.localizedExplanation,
    required this.eligibleSchemes,
  });

  factory ArbitrageAnalysisResult.fromJson(Map<String, dynamic> json) {
    var rawAlts = json['alternative_mandis'] as List<dynamic>? ?? [];
    List<MandiArbitrageOption> alts = rawAlts.map((e) => MandiArbitrageOption.fromJson(e as Map<String, dynamic>)).toList();

    var rawSchemes = json['eligible_schemes'] as List<dynamic>? ?? [];
    List<SchemeCardData> schemes = rawSchemes.map((e) => SchemeCardData.fromJson(e as Map<String, dynamic>)).toList();

    return ArbitrageAnalysisResult(
      sessionId: json['session_id'] as String? ?? '',
      commodity: json['commodity'] as String? ?? 'Tomato',
      quantity: (json['quantity'] as num?)?.toDouble() ?? 20.0,
      unit: json['unit'] as String? ?? 'quintal',
      originCity: json['origin_city'] as String? ?? 'Kolhapur',
      originLat: (json['origin_lat'] as num?)?.toDouble() ?? 16.6913,
      originLon: (json['origin_lon'] as num?)?.toDouble() ?? 74.2432,
      vehicleType: json['vehicle_type'] as String? ?? 'bolero_pickup',
      recommendedMandi: MandiArbitrageOption.fromJson(json['recommended_mandi'] as Map<String, dynamic>? ?? {}),
      alternativeMandis: alts,
      bestTimeToSell: json['best_time_to_sell'] as String? ?? 'SELL_TODAY',
      predictionRationale: json['prediction_rationale'] as String? ?? '',
      localizedExplanation: json['localized_explanation'] as String? ?? '',
      eligibleSchemes: schemes,
    );
  }
}

class CommunityReportItem {
  final int id;
  final String mandiId;
  final String mandiName;
  final String commodity;
  final double priceReceived;
  final String farmerName;
  final String timestamp;

  CommunityReportItem({
    required this.id,
    required this.mandiId,
    required this.mandiName,
    required this.commodity,
    required this.priceReceived,
    required this.farmerName,
    required this.timestamp,
  });

  factory CommunityReportItem.fromJson(Map<String, dynamic> json) {
    return CommunityReportItem(
      id: json['id'] as int? ?? 0,
      mandiId: json['mandi_id'] as String? ?? '',
      mandiName: json['mandi_name'] as String? ?? '',
      commodity: json['commodity'] as String? ?? '',
      priceReceived: (json['price_received'] as num?)?.toDouble() ?? 0.0,
      farmerName: json['farmer_name'] as String? ?? 'Kisan Mitra',
      timestamp: json['timestamp'] as String? ?? '',
    );
  }
}
