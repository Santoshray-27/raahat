import 'package:flutter/material.dart';

import 'package:raahat/services/api_client.dart';
import 'package:raahat/core/location/location_service.dart';
import 'package:raahat/services/emergency_service.dart';
import 'package:raahat/core/constants/enums.dart';

/// Interactive emergency reporting screen using mock-driven analysis.
class EmergencyScreen extends StatefulWidget {
  const EmergencyScreen({super.key});

  @override
  State<EmergencyScreen> createState() => _EmergencyScreenState();
}

class _EmergencyScreenState extends State<EmergencyScreen> {
  final TextEditingController _inputController = TextEditingController();
  bool _isLoading = false;
  Map<String, dynamic>? _response;
  String? _validationError;

  final EmergencyService _emergencyService = EmergencyService(
    apiClient: ApiClient(),
    locationService: LocationService(),
  );

  static const List<String> _quickSelectExamples = [
    'I have a flat tire',
    'Accident with injuries',
    'My vehicle broke down',
    'I need fuel',
  ];

  @override
  void dispose() {
    _inputController.dispose();
    super.dispose();
  }

  void _onQuickSelectTap(String exampleText) {
    _inputController.text = exampleText;
    _inputController.selection = TextSelection.fromPosition(
      TextPosition(offset: exampleText.length),
    );
    if (_validationError != null) {
      setState(() {
        _validationError = null;
      });
    }
  }

  Future<void> _handleSubmit() async {
    final text = _inputController.text.trim();
    if (text.isEmpty) {
      setState(() {
        _validationError = 'Please describe your emergency before submitting.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please describe what happened before submitting.'),
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _validationError = null;
    });

    try {
      final responseMap = await _emergencyService.submitEmergency(text, NetworkMode.ONLINE);

      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _response = responseMap;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _validationError = 'Error: ${e.toString()}';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to submit emergency: ${e.toString()}'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  void _resetReport() {
    setState(() {
      _inputController.clear();
      _response = null;
      _validationError = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Emergency'),
        actions: [
          if (_response != null)
            IconButton(
              onPressed: _resetReport,
              icon: const Icon(Icons.refresh),
              tooltip: 'New Report',
            ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Emergency Input Card
              _buildInputCard(theme),
              const SizedBox(height: 16),

              // Mock Response Results
              if (_isLoading) _buildLoadingCard(theme),
              if (_response != null && !_isLoading)
                _buildResponseCard(theme, _response!),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Report Emergency',
              style: theme.textTheme.headlineMedium,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _inputController,
              maxLines: 4,
              enabled: !_isLoading,
              style: theme.textTheme.bodyLarge,
              decoration: InputDecoration(
                hintText: 'Tell RAAHAT what happened...',
                hintStyle: TextStyle(color: theme.colorScheme.onSurfaceVariant),
                errorText: _validationError,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: theme.colorScheme.outline),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: theme.colorScheme.primary,
                    width: 2,
                  ),
                ),
                contentPadding: const EdgeInsets.all(16),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Quick Select Examples:',
              style: theme.textTheme.labelLarge,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _quickSelectExamples.map((example) {
                return ActionChip(
                  label: Text(example),
                  onPressed: _isLoading ? null : () => _onQuickSelectTap(example),
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _handleSubmit,
              child: _isLoading
                  ? const SizedBox(
                      height: 24,
                      width: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: Colors.white,
                      ),
                    )
                  : const Text('SUBMIT'),
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
              'Analyzing Emergency Situation...',
              style: theme.textTheme.titleMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResponseCard(ThemeData theme, Map<String, dynamic> response) {
    // Extract real backend fields
    final incident = response['incident'] as Map<String, dynamic>? ?? {};
    final guidance = response['guidance'] as Map<String, dynamic>? ?? {};
    final ai = response['ai'] as Map<String, dynamic>? ?? {};
    final actions = response['recommended_actions'] as List<dynamic>? ?? [];

    final String incidentType = incident['category'] as String? ?? 'UNKNOWN';
    final String severity = incident['severity'] as String? ?? 'UNKNOWN';
    final double confidence = (ai['confidence_score'] as num?)?.toDouble() ?? 0.0;
    final String summary = guidance['summary'] as String? ?? (incident['description_summary'] as String? ?? 'Emergency reported.');

    final List<dynamic> stepsRaw = guidance['steps'] as List<dynamic>? ?? [];
    final List<String> guidanceSteps = stepsRaw.map((s) => (s['instruction'] as String?) ?? '').where((s) => s.isNotEmpty).toList();

    final List<dynamic> dontDoRaw = guidance['immediate_do_not_do'] as List<dynamic>? ?? [];
    final String safetyNote = dontDoRaw.join('\n');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [

        // Incident Overview Alert Card
        Card(
          color: const Color(0xFFFFF3E0),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.primary,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        incidentType,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE65100),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        'SEVERITY: $severity',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  summary,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontSize: 18,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Confidence: ${(confidence * 100).toStringAsFixed(0)}%',
                  style: theme.textTheme.bodyMedium,
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Guidance Title & Steps
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.shield_outlined,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Immediate Guidance',
                        style: theme.textTheme.titleLarge,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ...guidanceSteps.asMap().entries.map((entry) {
                  final index = entry.key + 1;
                  final step = entry.value;
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: theme.colorScheme.outlineVariant,
                      ),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        CircleAvatar(
                          radius: 14,
                          backgroundColor: theme.colorScheme.primary,
                          child: Text(
                            '$index',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            step,
                            style: theme.textTheme.bodyLarge,
                          ),
                        ),
                      ],
                    ),
                  );
                }),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Safety Note Warning Card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFFFFEBEE),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: const Color(0xFFD32F2F),
              width: 1.5,
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(
                Icons.warning_amber_rounded,
                color: Color(0xFFD32F2F),
                size: 26,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'SAFETY NOTE',
                      style: TextStyle(
                        color: Color(0xFFD32F2F),
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      safetyNote.isEmpty ? 'Follow guidance steps carefully.' : safetyNote,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFF5D4037),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Recommended Actions Section
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Recommended Actions',
                  style: theme.textTheme.titleMedium,
                ),
                const SizedBox(height: 12),
                Row(
                  children: actions.isEmpty
                      ? [const Text('No immediate actions recommended.')]
                      : actions.map((action) {
                          final label = (action['label'] as String?) ?? 'ACTION';
                          final actionType = (action['action_type'] as String?) ?? 'CALL';

                          IconData iconData = Icons.call;
                          if (actionType == 'NAVIGATE') iconData = Icons.navigation;
                          if (actionType == 'CALL_TOWING') iconData = Icons.car_repair;
                          if (actionType == 'CALL_POLICE') iconData = Icons.local_police;

                          return Expanded(
                            child: Padding(
                              padding: const EdgeInsets.only(right: 8.0),
                              child: ElevatedButton.icon(
                                onPressed: () {},
                                icon: Icon(iconData),
                                label: Text(label),
                              ),
                            ),
                          );
                        }).toList(),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
