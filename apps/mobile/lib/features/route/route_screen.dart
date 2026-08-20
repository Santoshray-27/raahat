import 'package:flutter/material.dart';

/// Screen for planning safe emergency and evacuation routes.
class RouteScreen extends StatefulWidget {
  const RouteScreen({super.key});

  @override
  State<RouteScreen> createState() => _RouteScreenState();
}

class _RouteScreenState extends State<RouteScreen> {
  late final TextEditingController _originController;
  late final TextEditingController _destinationController;

  bool _isCalculating = false;
  bool _hasRouteResult = false;
  String? _validationError;

  @override
  void initState() {
    super.initState();
    _originController = TextEditingController(text: 'My Current Location');
    _destinationController = TextEditingController(text: 'Bhopal');
  }

  @override
  void dispose() {
    _originController.dispose();
    _destinationController.dispose();
    super.dispose();
  }

  Future<void> _handlePlanJourney() async {
    final origin = _originController.text.trim();
    final destination = _destinationController.text.trim();

    if (origin.isEmpty || destination.isEmpty) {
      setState(() {
        _validationError = 'Please specify both Origin and Destination.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please specify both Origin and Destination.'),
        ),
      );
      return;
    }

    setState(() {
      _isCalculating = true;
      _validationError = null;
    });

    await Future.delayed(const Duration(seconds: 1));

    if (!mounted) return;

    setState(() {
      _isCalculating = false;
      _hasRouteResult = true;
    });
  }

  void _handlePrepareOfflinePack() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'Offline Pack navigation will be connected during the navigation integration task.',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Route Planner'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Inputs Card
              _buildInputsCard(theme),
              const SizedBox(height: 16),

              // Loading Card
              if (_isCalculating) _buildLoadingCard(theme),

              // Route Summary Result Card
              if (_hasRouteResult && !_isCalculating)
                _buildRouteSummaryCard(theme),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputsCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Evacuation & Emergency Route',
              style: theme.textTheme.headlineMedium,
            ),
            const SizedBox(height: 4),
            Text(
              'Enter your starting point and destination to find the safest route.',
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),

            // Origin Field
            TextField(
              controller: _originController,
              enabled: !_isCalculating,
              style: theme.textTheme.bodyLarge,
              decoration: InputDecoration(
                labelText: 'Origin',
                hintText: 'My Current Location',
                prefixIcon: Icon(
                  Icons.my_location,
                  color: theme.colorScheme.primary,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 14,
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Destination Field
            TextField(
              controller: _destinationController,
              enabled: !_isCalculating,
              style: theme.textTheme.bodyLarge,
              decoration: InputDecoration(
                labelText: 'Destination',
                hintText: 'e.g., Bhopal',
                errorText: _validationError,
                prefixIcon: Icon(
                  Icons.location_on,
                  color: theme.colorScheme.primary,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 14,
                ),
              ),
            ),
            const SizedBox(height: 16),

            // PLAN JOURNEY Button
            ElevatedButton.icon(
              onPressed: _isCalculating ? null : _handlePlanJourney,
              icon: const Icon(Icons.route),
              label: _isCalculating
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text('PLAN JOURNEY'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(
              'Calculating Safest Evacuation Route...',
              style: theme.textTheme.titleMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRouteSummaryCard(ThemeData theme) {
    final originText = _originController.text.trim() == 'My Current Location'
        ? 'Indore'
        : _originController.text.trim();
    final destText = _destinationController.text.trim();

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: theme.colorScheme.primary.withAlpha(80),
          width: 1.5,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header: Route title
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primaryContainer,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.alt_route,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'ROUTE SUMMARY',
                        style: theme.textTheme.labelLarge?.copyWith(
                          color: theme.colorScheme.primary,
                          fontSize: 11,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '$originText ➔ $destText',
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 12),

            // Distance & Duration Metrics Row
            Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          Icons.straighten,
                          color: theme.colorScheme.primary,
                          size: 24,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'DISTANCE',
                          style: theme.textTheme.labelLarge?.copyWith(
                            fontSize: 10,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '192 km',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          Icons.access_time,
                          color: theme.colorScheme.primary,
                          size: 24,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'EST. DURATION',
                          style: theme.textTheme.labelLarge?.copyWith(
                            fontSize: 10,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '3 hours 45 mins',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Warning-styled CTA Button
            ElevatedButton.icon(
              onPressed: _handlePrepareOfflinePack,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFE65100),
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 54),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 3,
              ),
              icon: const Icon(Icons.download_for_offline, size: 22),
              label: const Text(
                'Prepare Offline Safety Pack',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.5,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
