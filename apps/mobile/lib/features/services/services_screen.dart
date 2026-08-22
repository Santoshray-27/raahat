import 'package:flutter/material.dart';
import 'package:raahat/services/api_client.dart';
import 'package:raahat/core/location/location_service.dart';
import 'package:raahat/services/services_service.dart';

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
        return 'ALL';
      case 'HOSPITAL':
        return 'HOSPITAL';
      case 'MECHANIC':
        return 'MECHANIC';
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
    final services = _filteredServices;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Nearby Services'),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Column(
                children: [
                  // Location Banner
                  _buildLocationBanner(theme),
                  const SizedBox(height: 12),

                  // Category Filter Chips
                  _buildCategoryFilter(theme),
                ],
              ),
            ),
            const Divider(height: 1),

            // Services List
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _errorMessage != null
                      ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(32.0),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.error_outline, size: 48, color: Colors.red),
                                const SizedBox(height: 16),
                                Text(
                                  'Failed to load nearby services:\n$_errorMessage',
                                  textAlign: TextAlign.center,
                                  style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.error),
                                ),
                                const SizedBox(height: 16),
                                ElevatedButton.icon(
                                  onPressed: _fetchServices,
                                  icon: const Icon(Icons.refresh),
                                  label: const Text('Retry'),
                                ),
                              ],
                            ),
                          ),
                        )
                      : services.isEmpty
                          ? Center(child: _buildEmptyState(theme))
                          : ListView.builder(
                              padding: const EdgeInsets.all(16),
                              itemCount: services.length,
                              itemBuilder: (context, index) {
                                return _buildServiceCard(theme, services[index]);
                              },
                            ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationBanner(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.primary.withAlpha(50),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.my_location,
            color: theme.colorScheme.primary,
            size: 22,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'CURRENT LOCATION',
                      style: theme.textTheme.labelLarge?.copyWith(
                        color: theme.colorScheme.primary,
                        fontSize: 11,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      '(Demo / Mock)',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                        fontSize: 11,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  'Indore (22.7196° N, 75.8577° E)',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
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
      height: 40,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: _categories.length,
        separatorBuilder: (context, index) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final category = _categories[index];
          final isSelected = _selectedCategory == category;
          return FilterChip(
            selected: isSelected,
            label: Text(_formatCategoryLabel(category)),
            labelStyle: TextStyle(
              color: isSelected
                  ? Colors.white
                  : theme.colorScheme.onSurfaceVariant,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              fontSize: 12,
            ),
            selectedColor: theme.colorScheme.primary,
            backgroundColor: theme.colorScheme.surfaceContainerHighest,
            showCheckmark: false,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            onSelected: (selected) {
              if (selected) {
                setState(() {
                  _selectedCategory = category;
                });
              }
            },
          );
        },
      ),
    );
  }

  Widget _buildServiceCard(ThemeData theme, Map<String, dynamic> service) {
    final String name = service['name'] as String? ?? 'Unknown Provider';

    // category comes from service_types[0]
    final List<dynamic>? serviceTypes = service['service_types'] as List<dynamic>?;
    final String category = (serviceTypes != null && serviceTypes.isNotEmpty)
        ? serviceTypes.first.toString()
        : 'SERVICE';

    // address comes from address.formatted_address
    final Map<String, dynamic>? addressMap = service['address'] as Map<String, dynamic>?;
    final String address = addressMap?['formatted_address'] as String? ?? 'No address provided';

    // phone comes from contact.phone_primary
    final Map<String, dynamic>? contactMap = service['contact'] as Map<String, dynamic>?;
    final String phone = contactMap?['phone_primary'] as String? ?? 'No phone provided';

    final num? distanceKmNum = service['distance_km'] as num?;
    final double? rating = (service['rating'] as num?)?.toDouble();
    final String availabilityStatus =
        service['availability_status'] as String? ?? 'UNKNOWN';

    final String distanceKmText = distanceKmNum != null
        ? '${distanceKmNum.toStringAsFixed(1)} km'
        : 'N/A';

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Row: Category Badge & Distance
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.secondaryContainer,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    category,
                    style: TextStyle(
                      color: theme.colorScheme.onSecondaryContainer,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
                Row(
                  children: [
                    Icon(
                      Icons.near_me,
                      size: 16,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      distanceKmText,
                      style: theme.textTheme.labelLarge?.copyWith(
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 10),

            // Name & Rating
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    name,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontSize: 18,
                    ),
                  ),
                ),
                if (rating != null) ...[
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.amber.shade100,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.star,
                          size: 16,
                          color: Colors.amber,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          rating.toStringAsFixed(1),
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                            color: Colors.black87,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 8),

            // Address
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.location_on_outlined,
                  size: 18,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    address,
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),

            // Phone (Tappable)
            InkWell(
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Call feature will be connected later.'),
                  ),
                );
              },
              borderRadius: BorderRadius.circular(6),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.phone,
                      size: 18,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      phone,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.bold,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),

            // Status & Availability Row
            Row(
              children: [
                if (availabilityStatus == 'OPEN')
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8F5E9),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: const Color(0xFF2E7D32)),
                    ),
                    child: const Text(
                      'Open Now',
                      style: TextStyle(
                        color: Color(0xFF2E7D32),
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                  )
                else if (availabilityStatus == 'CLOSED')
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFEBEE),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: const Color(0xFFC62828)),
                    ),
                    child: const Text(
                      'Closed',
                      style: TextStyle(
                        color: Color(0xFFC62828),
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                  ),

                if (availabilityStatus == 'UNKNOWN')
                  Text(
                    'Availability unknown',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                    ),
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
      padding: const EdgeInsets.all(32.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search_off,
            size: 48,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: 16),
          Text(
            'No services found for this category.',
            style: theme.textTheme.titleMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
