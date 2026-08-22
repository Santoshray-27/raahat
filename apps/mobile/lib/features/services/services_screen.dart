import 'package:flutter/material.dart';
import 'package:raahat/services/api_client.dart';
import 'package:raahat/core/location/location_service.dart';
import 'package:raahat/services/services_service.dart';
import 'package:raahat/core/theme/design_tokens.dart';
import 'package:raahat/core/theme/raahat_widgets.dart';

/// Screen listing nearby emergency services from the backend API.
class ServicesScreen extends StatefulWidget {
  const ServicesScreen({super.key});

  @override
  State<ServicesScreen> createState() => _ServicesScreenState();
}

class _ServicesScreenState extends State<ServicesScreen> {
  String _selectedCategory = 'ALL';

  static const List<String> _categories = [
    'ALL',
    'HOSPITAL',
    'MECHANIC',
    'TOWING',
    'PUNCTURE_REPAIR',
  ];

  List<Map<String, dynamic>> _services = [];
  bool _isLoading = true;
  String? _errorMessage;

  late final ServicesService _servicesService;

  @override
  void initState() {
    super.initState();
    _servicesService = ServicesService(
      apiClient: ApiClient.instance,
      locationService: LocationService(),
    );
    _fetchServices();
  }

  Future<void> _fetchServices() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final results = await _servicesService.fetchNearbyServices('ALL');
      if (!mounted) return;
      setState(() {
        _services = results;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  List<Map<String, dynamic>> get _filteredServices {
    if (_selectedCategory == 'ALL') {
      return _services;
    }
    return _services
        .where((service) {
          final types = service['service_types'] as List<dynamic>?;
          return types != null && types.contains(_selectedCategory);
        })
        .toList();
  }

  String _formatCategoryLabel(String category) {
    switch (category) {
      case 'ALL':
        return 'ALL SERVICES';
      case 'HOSPITAL':
        return 'HOSPITALS';
      case 'MECHANIC':
        return 'MECHANICS';
      case 'TOWING':
        return 'TOWING';
      case 'PUNCTURE_REPAIR':
        return 'PUNCTURE REPAIR';
      default:
        return category;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final mediaQuery = MediaQuery.of(context);
    final isSmallScreen = mediaQuery.size.width < 380;
    final services = _filteredServices;

    return Scaffold(
      backgroundColor: RaahatColors.canvasBackground,
      appBar: AppBar(
        backgroundColor: RaahatColors.whiteCard,
        elevation: 0,
        title: Text(
          'Nearby Providers',
          style: RaahatTypography.cardTitle(
            color: RaahatColors.textPrimary,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: RaahatColors.primaryBlue),
            onPressed: _fetchServices,
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: Column(
              children: [
                Padding(
                  padding: EdgeInsets.fromLTRB(
                    isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg,
                    RaahatSpacing.base,
                    isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg,
                    RaahatSpacing.sm,
                  ),
                  child: Column(
                    children: [
                      // Location Status Strip / Banner
                      _buildLocationBanner(theme),
                      const SizedBox(height: RaahatSpacing.md),

                      // Category Filter Chips
                      _buildCategoryFilter(theme),
                    ],
                  ),
                ),
                const Divider(height: 1, color: RaahatColors.border),

                // Services List
                Expanded(
                  child: _isLoading
                      ? const Center(
                          child: CircularProgressIndicator(
                            color: RaahatColors.primaryBlue,
                          ),
                        )
                      : _errorMessage != null
                          ? Center(
                              child: Padding(
                                padding: const EdgeInsets.all(RaahatSpacing.xl2),
                                child: Container(
                                  padding: const EdgeInsets.all(RaahatSpacing.lg2),
                                  decoration: BoxDecoration(
                                    color: RaahatColors.whiteCard,
                                    borderRadius: BorderRadius.circular(RaahatRadius.mainCard),
                                    border: Border.all(color: RaahatColors.redBorder),
                                    boxShadow: RaahatShadows.card,
                                  ),
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(
                                        Icons.error_outline_rounded,
                                        size: 44,
                                        color: RaahatColors.emergencyRed,
                                      ),
                                      const SizedBox(height: RaahatSpacing.base),
                                      Text(
                                        'Failed to Load Services',
                                        style: RaahatTypography.cardTitle(
                                          color: RaahatColors.textPrimary,
                                        ),
                                      ),
                                      const SizedBox(height: RaahatSpacing.xs),
                                      Text(
                                        _errorMessage!,
                                        textAlign: TextAlign.center,
                                        style: RaahatTypography.bodySmall(
                                          color: RaahatColors.emergencyRed,
                                        ),
                                      ),
                                      const SizedBox(height: RaahatSpacing.lg),
                                      ElevatedButton.icon(
                                        onPressed: _fetchServices,
                                        icon: const Icon(Icons.refresh),
                                        label: const Text('RETRY SEARCH'),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            )
                          : services.isEmpty
                              ? Center(child: _buildEmptyState(theme))
                              : ListView.builder(
                                  padding: EdgeInsets.all(
                                    isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg,
                                  ),
                                  itemCount: services.length,
                                  itemBuilder: (context, index) {
                                    return _buildServiceCard(theme, services[index]);
                                  },
                                ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLocationBanner(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: RaahatSpacing.base,
        vertical: RaahatSpacing.md,
      ),
      decoration: BoxDecoration(
        color: RaahatColors.blueLight,
        borderRadius: BorderRadius.circular(RaahatRadius.card),
        border: Border.all(color: RaahatColors.blueBorder),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: RaahatColors.primaryBlue.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.my_location_rounded,
              color: RaahatColors.primaryBlue,
              size: 20,
            ),
          ),
          const SizedBox(width: RaahatSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'GPS SEARCH RADIUS (5.0 KM)',
                  style: RaahatTypography.mono(
                    color: RaahatColors.primaryBlue,
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: RaahatSpacing.xs2),
                Text(
                  'Indore Coordinates (22.7196° N, 75.8577° E)',
                  style: RaahatTypography.cardTitle().copyWith(fontSize: 13),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryFilter(ThemeData theme) {
    return SizedBox(
      height: 42,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: _categories.length,
        separatorBuilder: (context, index) => const SizedBox(width: RaahatSpacing.sm),
        itemBuilder: (context, index) {
          final category = _categories[index];
          final isSelected = _selectedCategory == category;
          return RaahatCategoryChip(
            label: _formatCategoryLabel(category),
            isSelected: isSelected,
            onTap: () {
              setState(() {
                _selectedCategory = category;
              });
            },
          );
        },
      ),
    );
  }

  Widget _buildServiceCard(ThemeData theme, Map<String, dynamic> service) {
    final String name = service['name'] as String? ?? 'Unknown Provider';

    final List<dynamic>? serviceTypes = service['service_types'] as List<dynamic>?;
    final String category = (serviceTypes != null && serviceTypes.isNotEmpty)
        ? serviceTypes.first.toString()
        : 'SERVICE';

    final Map<String, dynamic>? addressMap = service['address'] as Map<String, dynamic>?;
    final String address = addressMap?['formatted_address'] as String? ?? 'No address provided';

    final Map<String, dynamic>? contactMap = service['contact'] as Map<String, dynamic>?;
    final String phone = contactMap?['phone_primary'] as String? ?? 'No phone provided';

    final num? distanceKmNum = service['distance_km'] as num?;
    final double? rating = (service['rating'] as num?)?.toDouble();
    final String availabilityStatus =
        service['availability_status'] as String? ?? 'UNKNOWN';

    final String distanceKmText = distanceKmNum != null
        ? '${distanceKmNum.toStringAsFixed(1)} km'
        : 'N/A';

    return Padding(
      padding: const EdgeInsets.only(bottom: RaahatSpacing.base),
      child: RaahatLightCard(
        padding: const EdgeInsets.all(RaahatSpacing.base),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Row: Category Badge & Distance
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: RaahatSpacing.sm2,
                      vertical: RaahatSpacing.xs,
                    ),
                    decoration: BoxDecoration(
                      color: RaahatColors.blueLight,
                      borderRadius: BorderRadius.circular(RaahatRadius.badge),
                      border: Border.all(color: RaahatColors.blueBorder),
                    ),
                    child: Text(
                      category.replaceAll('_', ' '),
                      style: RaahatTypography.eyebrow(
                        color: RaahatColors.primaryBlue,
                      ).copyWith(fontSize: 11),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
                const SizedBox(width: RaahatSpacing.sm),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.near_me_rounded,
                      size: 15,
                      color: RaahatColors.primaryBlue,
                    ),
                    const SizedBox(width: RaahatSpacing.xs),
                    Text(
                      distanceKmText,
                      style: RaahatTypography.mono(
                        color: RaahatColors.primaryBlue,
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: RaahatSpacing.md),

            // Name & Rating
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    name,
                    style: RaahatTypography.cardTitle(
                      color: RaahatColors.textPrimary,
                    ).copyWith(fontSize: 16),
                  ),
                ),
                if (rating != null) ...[
                  const SizedBox(width: RaahatSpacing.sm),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: RaahatSpacing.sm,
                      vertical: RaahatSpacing.xs2,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFFBEB),
                      borderRadius: BorderRadius.circular(RaahatRadius.badge),
                      border: Border.all(color: RaahatColors.amberWarning.withValues(alpha: 0.4)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.star_rounded,
                          size: 15,
                          color: RaahatColors.amberWarning,
                        ),
                        const SizedBox(width: 3),
                        Text(
                          rating.toStringAsFixed(1),
                          style: RaahatTypography.mono(
                            color: const Color(0xFF92400E),
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: RaahatSpacing.sm),

            // Address
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.location_on_outlined,
                  size: 18,
                  color: RaahatColors.textMuted,
                ),
                const SizedBox(width: RaahatSpacing.sm),
                Expanded(
                  child: Text(
                    address,
                    style: RaahatTypography.bodySmall(
                      color: RaahatColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: RaahatSpacing.sm2),

            // Phone & Status Row
            Wrap(
              spacing: RaahatSpacing.md,
              runSpacing: RaahatSpacing.sm,
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                // Phone (Tappable)
                InkWell(
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Calling $phone')),
                    );
                  },
                  borderRadius: BorderRadius.circular(RaahatRadius.button),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: RaahatSpacing.sm2,
                      vertical: RaahatSpacing.xs,
                    ),
                    decoration: BoxDecoration(
                      color: RaahatColors.blueLight,
                      borderRadius: BorderRadius.circular(RaahatRadius.button),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.phone_outlined,
                          size: 16,
                          color: RaahatColors.primaryBlue,
                        ),
                        const SizedBox(width: RaahatSpacing.xs),
                        Text(
                          phone,
                          style: RaahatTypography.mono(
                            color: RaahatColors.primaryBlue,
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Availability Status Badge
                if (availabilityStatus == 'OPEN')
                  const RaahatLiveBadge(label: 'OPEN NOW')
                else if (availabilityStatus == 'CLOSED')
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: RaahatSpacing.sm,
                      vertical: RaahatSpacing.xs,
                    ),
                    decoration: BoxDecoration(
                      color: RaahatColors.redLight,
                      borderRadius: BorderRadius.circular(RaahatRadius.badge),
                    ),
                    child: Text(
                      'CLOSED',
                      style: RaahatTypography.monoBadge(
                        color: RaahatColors.emergencyRed,
                      ),
                    ),
                  )
                else
                  Text(
                    'Status Unknown',
                    style: RaahatTypography.bodySmall(
                      color: RaahatColors.textMuted,
                    ).copyWith(fontStyle: FontStyle.italic, fontSize: 11),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.all(RaahatSpacing.xl2),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(RaahatSpacing.base),
            decoration: const BoxDecoration(
              color: RaahatColors.mutedBackground,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.search_off_rounded,
              size: 40,
              color: RaahatColors.textMuted,
            ),
          ),
          const SizedBox(height: RaahatSpacing.base),
          Text(
            'No Services Found',
            style: RaahatTypography.cardTitle(
              color: RaahatColors.textPrimary,
            ),
          ),
          const SizedBox(height: RaahatSpacing.xs),
          Text(
            'No matching providers discovered within this search category.',
            style: RaahatTypography.bodySmall(
              color: RaahatColors.textMuted,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
