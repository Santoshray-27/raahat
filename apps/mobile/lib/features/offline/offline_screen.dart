import 'package:flutter/material.dart';

/// Screen for managing simulated offline packs and on-device AI status.
class OfflineScreen extends StatefulWidget {
  const OfflineScreen({super.key});

  @override
  State<OfflineScreen> createState() => _OfflineScreenState();
}

class _OfflineScreenState extends State<OfflineScreen> {
  bool _isDownloading = false;
  bool _isInstalled = false;
  double _downloadProgress = 0.0;
  String _downloadStatusText = '';

  Future<void> _startDownloadSimulation() async {
    setState(() {
      _isDownloading = true;
      _isInstalled = false;
      _downloadProgress = 0.0;
      _downloadStatusText = 'Initializing Download...';
    });

    await Future.delayed(const Duration(milliseconds: 400));
    if (!mounted) return;

    setState(() {
      _downloadProgress = 0.25;
      _downloadStatusText = 'Downloading Route Map...';
    });

    await Future.delayed(const Duration(milliseconds: 600));
    if (!mounted) return;

    setState(() {
      _downloadProgress = 0.55;
      _downloadStatusText = 'Caching Local Providers...';
    });

    await Future.delayed(const Duration(milliseconds: 600));
    if (!mounted) return;

    setState(() {
      _downloadProgress = 0.80;
      _downloadStatusText = 'Assembling Offline RAG Index...';
    });

    await Future.delayed(const Duration(milliseconds: 500));
    if (!mounted) return;

    setState(() {
      _downloadProgress = 0.95;
      _downloadStatusText = 'Verifying Pack Checksum...';
    });

    await Future.delayed(const Duration(milliseconds: 400));
    if (!mounted) return;

    setState(() {
      _downloadProgress = 1.0;
      _downloadStatusText = 'Offline Safety Pack Installed Successfully!';
      _isDownloading = false;
      _isInstalled = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Offline Packs'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Demo Notice Banner
              _buildDemoNoticeBanner(theme),
              const SizedBox(height: 16),

              // On-Device AI Status Board
              _buildAiStatusBoard(theme),
              const SizedBox(height: 16),

              // Download / Manifest Section
              if (_isDownloading)
                _buildDownloadProgressCard(theme)
              else if (_isInstalled)
                _buildManifestCard(theme)
              else
                _buildInitialPackCard(theme),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDemoNoticeBanner(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: theme.colorScheme.primary.withAlpha(50),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.info_outline,
            size: 20,
            color: theme.colorScheme.onPrimaryContainer,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              'Demo Mode — On-device AI and offline packs are simulated locally.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onPrimaryContainer,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAiStatusBoard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.memory,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'On-Device AI & Engine Status',
                  style: theme.textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Gemma Model Status
            _buildStatusItem(
              theme: theme,
              label: 'Gemma Model Status',
              status: 'MODEL_READY',
              isGreen: true,
              icon: Icons.check_circle_outline,
            ),
            const SizedBox(height: 12),

            // Local RAG Index
            _buildStatusItem(
              theme: theme,
              label: 'Local RAG Index',
              status: 'OFFLINE_RAG_READY',
              isGreen: true,
              icon: Icons.storage_outlined,
            ),
            const SizedBox(height: 12),

            // Storage
            _buildStatusItem(
              theme: theme,
              label: 'Mobile Storage Used',
              status: '1.6 GB / 64 GB',
              isGreen: false,
              icon: Icons.sd_card_outlined,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusItem({
    required ThemeData theme,
    required String label,
    required String status,
    required bool isGreen,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: theme.colorScheme.outlineVariant,
        ),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: theme.colorScheme.onSurfaceVariant),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              label,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: isGreen ? const Color(0xFFE8F5E9) : theme.colorScheme.surface,
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: isGreen ? const Color(0xFF2E7D32) : theme.colorScheme.outline,
              ),
            ),
            child: Text(
              status,
              style: TextStyle(
                color: isGreen ? const Color(0xFF2E7D32) : theme.colorScheme.onSurface,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInitialPackCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Indore ➔ Bhopal Corridor Pack',
              style: theme.textTheme.headlineMedium?.copyWith(fontSize: 20),
            ),
            const SizedBox(height: 6),
            Text(
              'Includes offline map data, emergency providers, and vector RAG indices for zero-connectivity situations.',
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Chip(
                  avatar: const Icon(Icons.data_usage, size: 16),
                  label: const Text('Size: 36.4 MB'),
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                ),
                const SizedBox(width: 8),
                Chip(
                  avatar: const Icon(Icons.offline_pin_outlined, size: 16),
                  label: const Text('Pre-packaged'),
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                ),
              ],
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _startDownloadSimulation,
              icon: const Icon(Icons.download),
              label: const Text('DOWNLOAD SAFETY PACK'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDownloadProgressCard(ThemeData theme) {
    final progressPct = (_downloadProgress * 100).toInt();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2.5),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Installing Offline Pack...',
                    style: theme.textTheme.titleMedium,
                  ),
                ),
                Text(
                  '$progressPct%',
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: _downloadProgress,
                minHeight: 10,
                backgroundColor: theme.colorScheme.surfaceContainerHighest,
                color: theme.colorScheme.primary,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              _downloadStatusText,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontStyle: FontStyle.italic,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildManifestCard(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Success Banner
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFE8F5E9),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF2E7D32)),
          ),
          child: Row(
            children: [
              const Icon(
                Icons.check_circle,
                color: Color(0xFF2E7D32),
                size: 24,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Offline Safety Pack Installed Successfully!',
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: const Color(0xFF2E7D32),
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Manifest Details Card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'PACK MANIFEST',
                      style: theme.textTheme.labelLarge?.copyWith(
                        color: theme.colorScheme.primary,
                        letterSpacing: 0.5,
                        fontSize: 11,
                      ),
                    ),
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
                        'ACTIVE',
                        style: TextStyle(
                          color: Color(0xFF2E7D32),
                          fontWeight: FontWeight.bold,
                          fontSize: 11,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  'Indore ➔ Bhopal Corridor (15km radius)',
                  style: theme.textTheme.titleLarge?.copyWith(fontSize: 18),
                ),
                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 12),

                _buildManifestRow(
                  theme,
                  icon: Icons.sd_storage_outlined,
                  label: 'Package Size',
                  value: '36.4 MB',
                ),
                const SizedBox(height: 10),

                _buildManifestRow(
                  theme,
                  icon: Icons.local_hospital_outlined,
                  label: 'Included Data',
                  value: '8 Hospitals, 4 Police Stations, 12 Mechanics, 6 Puncture Shops',
                ),
                const SizedBox(height: 10),

                _buildManifestRow(
                  theme,
                  icon: Icons.sync,
                  label: 'Last Sync',
                  value: 'Just Now',
                ),
                const SizedBox(height: 20),

                OutlinedButton.icon(
                  onPressed: _startDownloadSimulation,
                  icon: const Icon(Icons.sync),
                  label: const Text('RE-SYNC SAFETY PACK'),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildManifestRow(
    ThemeData theme, {
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: theme.colorScheme.primary),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: theme.textTheme.labelLarge?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: theme.textTheme.bodyLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
