import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:raahat/services/api_client.dart';
import 'package:raahat/core/location/location_service.dart';
import 'package:raahat/services/emergency_service.dart';
import 'package:raahat/core/constants/enums.dart';
import 'package:raahat/core/theme/design_tokens.dart';
import 'package:raahat/core/theme/raahat_widgets.dart';

/// Interactive emergency reporting screen using situation-aware AI analysis.
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
  String? _conversationId;

  final EmergencyService _emergencyService = EmergencyService(
    apiClient: ApiClient.instance,
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
      final userId = FirebaseAuth.instance.currentUser?.uid;
      final responseMap = await _emergencyService.submitEmergency(
        text, 
        NetworkMode.ONLINE,
        conversationId: _conversationId,
        userId: userId,
      );

      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _response = responseMap;
        if (responseMap.containsKey('conversation_id') && responseMap['conversation_id'] != null) {
          _conversationId = responseMap['conversation_id'].toString();
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _validationError = 'Error: ${e.toString()}';
      });
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to submit emergency: ${e.toString()}'),
          backgroundColor: RaahatColors.emergencyRed,
        ),
      );
    }
  }

  void _resetReport() {
    setState(() {
      _inputController.clear();
      _response = null;
      _validationError = null;
      _conversationId = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final mediaQuery = MediaQuery.of(context);
    final isSmallScreen = mediaQuery.size.width < 380;
    final bool hasResponse = _response != null && !_isLoading;

    return Scaffold(
      backgroundColor: RaahatColors.canvasBackground,
      appBar: AppBar(
        backgroundColor: RaahatColors.whiteCard,
        elevation: 0,
        title: Text(
          'Emergency Triage',
          style: RaahatTypography.cardTitle(
            color: RaahatColors.textPrimary,
          ),
        ),
        actions: [
          if (hasResponse)
            TextButton.icon(
              onPressed: _resetReport,
              icon: const Icon(Icons.refresh, size: 18),
              label: const Text('New Report'),
              style: TextButton.styleFrom(
                foregroundColor: RaahatColors.primaryBlue,
              ),
            ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: SingleChildScrollView(
              padding: EdgeInsets.symmetric(
                horizontal: isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg,
                vertical: RaahatSpacing.base,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Status Strip
                  RaahatStatusStrip(
                    statusText: hasResponse
                        ? 'INCIDENT ACTIVE — DISPATCH QUEUED'
                        : 'GPS LOCATION LOCKED — READY TO TRIAGE',
                    isOnline: true,
                  ),
                  const SizedBox(height: RaahatSpacing.base),

                  // Input section — hidden once a response is received
                  if (!hasResponse) ...[
                    _buildConsoleInputSection(theme, isSmallScreen),
                    const SizedBox(height: RaahatSpacing.base),
                  ],

                  // Loading state
                  if (_isLoading) _buildLoadingState(theme),

                  // Response sections
                  if (hasResponse) _buildResponseSections(theme, _response!),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ─── CONSOLE INPUT SECTION ──────────────────────────────────────────────────

  Widget _buildConsoleInputSection(ThemeData theme, bool isSmallScreen) {
    return RaahatConsoleCard(
      padding: EdgeInsets.all(isSmallScreen ? RaahatSpacing.base : RaahatSpacing.lg2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: RaahatColors.emergencyRed.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(RaahatRadius.badge),
                    ),
                    child: const Icon(
                      Icons.edit_note_rounded,
                      color: RaahatColors.emergencyRed,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: RaahatSpacing.sm2),
                  Text(
                    'INCIDENT REPORT',
                    style: RaahatTypography.mono(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: RaahatColors.darkGold,
                    ),
                  ),
                ],
              ),
              const RaahatLiveBadge(label: 'AI READY'),
            ],
          ),
          const SizedBox(height: RaahatSpacing.base),
          Text(
            'Describe Your Emergency',
            style: RaahatTypography.displayH3(
              color: RaahatColors.darkText,
              fontSize: isSmallScreen ? 20 : 22,
            ),
          ),
          const SizedBox(height: RaahatSpacing.xs),
          Text(
            'Provide details: vehicle condition, injuries, landmarks, or immediate hazards.',
            style: RaahatTypography.bodySmall(
              color: RaahatColors.darkMuted,
            ),
          ),
          const SizedBox(height: RaahatSpacing.base),

          // Dark Console Input
          RaahatConsoleInput(
            controller: _inputController,
            maxLines: 4,
            enabled: !_isLoading,
            hintText: 'e.g. Broken axle on NH-52, 2 passengers, need roadside assistance...',
            errorText: _validationError,
          ),
          const SizedBox(height: RaahatSpacing.base),

          // Quick Select Pills
          Text(
            'Quick select presets:',
            style: RaahatTypography.mono(
              fontSize: 11,
              color: RaahatColors.darkMuted,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: RaahatSpacing.sm),
          Wrap(
            spacing: RaahatSpacing.sm,
            runSpacing: RaahatSpacing.sm,
            children: _quickSelectExamples.map((example) {
              final isMatch = _inputController.text == example;
              return RaahatCategoryChip(
                label: example,
                isSelected: isMatch,
                onTap: _isLoading ? null : () => _onQuickSelectTap(example),
              );
            }).toList(),
          ),
          const SizedBox(height: RaahatSpacing.lg),

          // SOS Submit Button
          RaahatSosButton(
            label: _isLoading ? 'SUBMITTING REPORT...' : 'REQUEST EMERGENCY HELP',
            isLoading: _isLoading,
            onPressed: _isLoading ? null : _handleSubmit,
          ),
        ],
      ),
    );
  }

  // ─── LOADING ───────────────────────────────────────────────────────────────

  Widget _buildLoadingState(ThemeData theme) {
    return RaahatConsoleCard(
      padding: const EdgeInsets.symmetric(
        horizontal: RaahatSpacing.lg2,
        vertical: RaahatSpacing.xl2,
      ),
      child: Column(
        children: [
          const CircularProgressIndicator(
            color: RaahatColors.emergencyRed,
            strokeWidth: 3,
          ),
          const SizedBox(height: RaahatSpacing.lg2),
          Text(
            'Analyzing Emergency Situation...',
            style: RaahatTypography.mono(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: RaahatColors.darkText,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: RaahatSpacing.sm),
          Text(
            'RAAHAT AI is calculating severity and assembling guidance...',
            style: RaahatTypography.bodySmall(
              color: RaahatColors.darkMuted,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  // ─── RESPONSE SECTIONS ─────────────────────────────────────────────────────

  Widget _buildResponseSections(
      ThemeData theme, Map<String, dynamic> response) {
    final incident = response['incident'] as Map<String, dynamic>? ?? {};
    final guidance = response['guidance'] as Map<String, dynamic>? ?? {};
    final ai = response['ai'] as Map<String, dynamic>? ?? {};
    final actions = response['recommended_actions'] as List<dynamic>? ?? [];

    final String incidentType =
        incident['category'] as String? ?? 'UNKNOWN';
    final String severity = incident['severity'] as String? ?? 'UNKNOWN';
    final double confidence =
        (ai['confidence_score'] as num?)?.toDouble() ?? 0.0;
    final String summary = guidance['summary'] as String? ??
        (incident['description_summary'] as String? ?? 'Emergency reported.');

    final List<dynamic> stepsRaw =
        guidance['steps'] as List<dynamic>? ?? [];
    final List<String> guidanceSteps = stepsRaw
        .map((s) => (s['instruction'] as String?) ?? '')
        .where((s) => s.isNotEmpty)
        .toList();

    final List<dynamic> dontDoRaw =
        guidance['immediate_do_not_do'] as List<dynamic>? ?? [];
    final String safetyNote = dontDoRaw.join('\n');
    final List<dynamic> services = response['services'] as List<dynamic>? ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Incident summary card
        _buildIncidentSummaryCard(theme, incidentType, severity, summary, confidence),
        const SizedBox(height: RaahatSpacing.base),

        // Guidance card
        if (guidanceSteps.isNotEmpty) ...[
          _buildGuidanceCard(theme, guidanceSteps),
          const SizedBox(height: RaahatSpacing.base),
        ],

        // Safety note
        if (safetyNote.isNotEmpty || dontDoRaw.isEmpty) ...[
          _buildSafetyNoteCard(theme, safetyNote),
          const SizedBox(height: RaahatSpacing.base),
        ],

        // Recommended actions
        if (actions.isNotEmpty) ...[
          _buildRecommendedActionsCard(theme, actions),
          const SizedBox(height: RaahatSpacing.base),
        ],

        // Nearby Services
        if (services.isNotEmpty) ...[
          _buildServicesCard(theme, services),
          const SizedBox(height: RaahatSpacing.base),
        ],

        // Error card if validation error persists
        if (_validationError != null)
          _buildErrorCard(theme, _validationError!),
      ],
    );
  }

  // ─── SERVICES CARD ─────────────────────────────────────────────────────────

  Widget _buildServicesCard(ThemeData theme, List<dynamic> services) {
    return RaahatLightCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: RaahatColors.primaryBlue.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.local_hospital_rounded,
                  color: RaahatColors.primaryBlue,
                  size: 20,
                ),
              ),
              const SizedBox(width: RaahatSpacing.sm2),
              Text(
                'Nearby Services',
                style: RaahatTypography.cardTitle(
                  color: RaahatColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: RaahatSpacing.base),
          ...services.map((service) {
            final name = service['name']?.toString() ?? 'Unknown Service';
            final type = service['service_type']?.toString() ?? '';
            final distance = service['distance'] != null ? '${service['distance']} km' : '';
            final address = service['address']?.toString() ?? '';
            final phone = service['phone']?.toString() ?? '';
            final eta = service['eta']?.toString() ?? '';
            final provider = service['provider']?.toString() ?? '';

            return Padding(
              padding: const EdgeInsets.only(bottom: RaahatSpacing.md),
              child: Container(
                padding: const EdgeInsets.all(RaahatSpacing.md),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(RaahatRadius.button),
                  border: Border.all(color: RaahatColors.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            name,
                            style: RaahatTypography.bodyRegular(
                              color: RaahatColors.textPrimary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        if (distance.isNotEmpty)
                          Text(
                            distance,
                            style: RaahatTypography.mono(
                              fontSize: 12,
                              color: RaahatColors.primaryBlue,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                      ],
                    ),
                    if (type.isNotEmpty || provider.isNotEmpty) ...[
                      const SizedBox(height: RaahatSpacing.xs),
                      Text(
                        [if (type.isNotEmpty) type, if (provider.isNotEmpty) 'via $provider'].join(' • '),
                        style: RaahatTypography.bodySmall(color: RaahatColors.textMuted),
                      ),
                    ],
                    if (address.isNotEmpty) ...[
                      const SizedBox(height: RaahatSpacing.sm),
                      Row(
                        children: [
                          const Icon(Icons.location_on_outlined, size: 14, color: RaahatColors.textMuted),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              address,
                              style: RaahatTypography.bodySmall(color: RaahatColors.textSecondary),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ],
                    if (phone.isNotEmpty) ...[
                      const SizedBox(height: RaahatSpacing.xs),
                      Row(
                        children: [
                          const Icon(Icons.phone_outlined, size: 14, color: RaahatColors.textMuted),
                          const SizedBox(width: 4),
                          Text(
                            phone,
                            style: RaahatTypography.bodySmall(color: RaahatColors.textSecondary),
                          ),
                        ],
                      ),
                    ],
                    if (eta.isNotEmpty) ...[
                      const SizedBox(height: RaahatSpacing.xs),
                      Row(
                        children: [
                          const Icon(Icons.timer_outlined, size: 14, color: RaahatColors.textMuted),
                          const SizedBox(width: 4),
                          Text(
                            'ETA: $eta',
                            style: RaahatTypography.bodySmall(color: RaahatColors.textSecondary),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  // ─── INCIDENT SUMMARY CARD ─────────────────────────────────────────────────

  Widget _buildIncidentSummaryCard(
    ThemeData theme,
    String incidentType,
    String severity,
    String summary,
    double confidence,
  ) {
    final Color severityColor = RaahatColors.severityColor(severity);

    return RaahatLightCard(
      borderColor: severityColor.withValues(alpha: 0.5),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            spacing: RaahatSpacing.sm,
            runSpacing: RaahatSpacing.xs,
            crossAxisAlignment: WrapCrossAlignment.center,
            alignment: WrapAlignment.spaceBetween,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: RaahatSpacing.sm2,
                      vertical: RaahatSpacing.xs,
                    ),
                    decoration: BoxDecoration(
                      color: RaahatColors.primaryBlue.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(RaahatRadius.badge),
                      border: Border.all(color: RaahatColors.primaryBlue.withValues(alpha: 0.3)),
                    ),
                    child: Text(
                      incidentType.replaceAll('_', ' '),
                      style: RaahatTypography.eyebrow(
                        color: RaahatColors.primaryBlue,
                      ).copyWith(fontSize: 11),
                    ),
                  ),
                  const SizedBox(width: RaahatSpacing.sm),
                  RaahatSeverityBadge(severity: severity),
                ],
              ),
              if (confidence > 0)
                Text(
                  '${(confidence * 100).toStringAsFixed(0)}% CONFIDENCE',
                  style: RaahatTypography.mono(
                    fontSize: 11,
                    color: RaahatColors.textMuted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
            ],
          ),
          const SizedBox(height: RaahatSpacing.base),
          Text(
            summary,
            style: RaahatTypography.cardTitle(
              color: RaahatColors.textPrimary,
            ).copyWith(height: 1.4),
          ),
        ],
      ),
    );
  }

  // ─── GUIDANCE CARD ─────────────────────────────────────────────────────────

  Widget _buildGuidanceCard(ThemeData theme, List<String> steps) {
    return RaahatLightCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: RaahatColors.primaryBlue.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.shield_outlined,
                  color: RaahatColors.primaryBlue,
                  size: 20,
                ),
              ),
              const SizedBox(width: RaahatSpacing.sm2),
              Text(
                'Action Guidance',
                style: RaahatTypography.cardTitle(
                  color: RaahatColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: RaahatSpacing.base),
          ...steps.asMap().entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.only(bottom: RaahatSpacing.md),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 26,
                    height: 26,
                    decoration: BoxDecoration(
                      color: RaahatColors.primaryBlue,
                      borderRadius: BorderRadius.circular(RaahatRadius.badge),
                    ),
                    child: Center(
                      child: Text(
                        '${entry.key + 1}',
                        style: RaahatTypography.monoBadge(
                          color: Colors.white,
                        ).copyWith(fontSize: 12),
                      ),
                    ),
                  ),
                  const SizedBox(width: RaahatSpacing.md),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 2.0),
                      child: Text(
                        entry.value,
                        style: RaahatTypography.bodyRegular(
                          color: RaahatColors.textPrimary,
                        ).copyWith(fontSize: 15),
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  // ─── SAFETY NOTE CARD ──────────────────────────────────────────────────────

  Widget _buildSafetyNoteCard(ThemeData theme, String safetyNote) {
    return Container(
      padding: const EdgeInsets.all(RaahatSpacing.base),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFBEB),
        borderRadius: BorderRadius.circular(RaahatRadius.mainCard),
        border: Border.all(color: RaahatColors.amberWarning.withValues(alpha: 0.4)),
        boxShadow: RaahatShadows.card,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: RaahatColors.amberWarning.withValues(alpha: 0.2),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.warning_amber_rounded,
              color: RaahatColors.amberWarning,
              size: 20,
            ),
          ),
          const SizedBox(width: RaahatSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'SAFETY PRECAUTIONS',
                  style: RaahatTypography.mono(
                    fontSize: 11,
                    color: const Color(0xFFB45309),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: RaahatSpacing.xs),
                Text(
                  safetyNote.isEmpty
                      ? 'Follow guidance steps carefully and remain in a safe location.'
                      : safetyNote,
                  style: RaahatTypography.bodySmall(
                    color: const Color(0xFF92400E),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── RECOMMENDED ACTIONS ───────────────────────────────────────────────────

  Widget _buildRecommendedActionsCard(
      ThemeData theme, List<dynamic> actions) {
    return RaahatLightCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: RaahatColors.primaryBlue.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.bolt_rounded,
                  color: RaahatColors.primaryBlue,
                  size: 20,
                ),
              ),
              const SizedBox(width: RaahatSpacing.sm2),
              Text(
                'Recommended Actions',
                style: RaahatTypography.cardTitle(
                  color: RaahatColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: RaahatSpacing.base),
          ...actions.map((action) {
            final label = (action['label'] as String?) ?? 'ACTION';
            final actionType = (action['action_type'] as String?) ?? 'CALL';
            final (icon, color) = _actionStyle(actionType);

            return Padding(
              padding: const EdgeInsets.only(bottom: RaahatSpacing.sm2),
              child: Material(
                color: color.withValues(alpha: 0.06),
                borderRadius: BorderRadius.circular(RaahatRadius.button),
                child: InkWell(
                  borderRadius: BorderRadius.circular(RaahatRadius.button),
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Action selected: $label')),
                    );
                  },
                  child: Container(
                    constraints: const BoxConstraints(minHeight: 48),
                    padding: const EdgeInsets.symmetric(
                      horizontal: RaahatSpacing.base,
                      vertical: RaahatSpacing.md,
                    ),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(RaahatRadius.button),
                      border: Border.all(color: color.withValues(alpha: 0.25)),
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(RaahatSpacing.sm),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(RaahatRadius.badge),
                          ),
                          child: Icon(icon, color: color, size: 20),
                        ),
                        const SizedBox(width: RaahatSpacing.md),
                        Expanded(
                          child: Text(
                            label,
                            style: RaahatTypography.cardTitle(
                              color: RaahatColors.textPrimary,
                            ).copyWith(fontSize: 15),
                          ),
                        ),
                        const Icon(
                          Icons.chevron_right,
                          color: RaahatColors.textMuted,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  // ─── ERROR CARD ────────────────────────────────────────────────────────────

  Widget _buildErrorCard(ThemeData theme, String error) {
    return Container(
      padding: const EdgeInsets.all(RaahatSpacing.base),
      decoration: BoxDecoration(
        color: RaahatColors.redLight,
        borderRadius: BorderRadius.circular(RaahatRadius.mainCard),
        border: Border.all(color: RaahatColors.redBorder),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.error_outline_rounded,
            color: RaahatColors.emergencyRed,
            size: 24,
          ),
          const SizedBox(width: RaahatSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Submission Issue',
                  style: RaahatTypography.cardTitle(
                    color: RaahatColors.emergencyRed,
                  ).copyWith(fontSize: 15),
                ),
                const SizedBox(height: RaahatSpacing.xs),
                Text(
                  error,
                  style: RaahatTypography.bodySmall(
                    color: RaahatColors.textPrimary,
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: RaahatSpacing.sm2),
                TextButton.icon(
                  onPressed: _handleSubmit,
                  icon: const Icon(Icons.refresh, size: 16),
                  label: const Text('Retry Submission'),
                  style: TextButton.styleFrom(
                    foregroundColor: RaahatColors.emergencyRed,
                    padding: EdgeInsets.zero,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── HELPERS ───────────────────────────────────────────────────────────────

  (IconData, Color) _actionStyle(String actionType) {
    switch (actionType.toUpperCase()) {
      case 'CALL_AMBULANCE':
      case 'CALL':
        return (Icons.local_hospital_outlined, RaahatColors.emergencyRed);
      case 'NAVIGATE':
        return (Icons.alt_route_rounded, RaahatColors.primaryBlue);
      case 'CALL_TOWING':
        return (Icons.car_repair_rounded, RaahatColors.amber);
      case 'CALL_POLICE':
        return (Icons.local_police_outlined, RaahatColors.textSecondary);
      default:
        return (Icons.phone_outlined, RaahatColors.primaryBlue);
    }
  }
}
