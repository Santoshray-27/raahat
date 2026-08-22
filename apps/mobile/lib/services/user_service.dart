import 'package:raahat/services/api_client.dart';

class UserService {
  final ApiClient apiClient;

  UserService({required this.apiClient});

  Future<Map<String, dynamic>> getMe() async {
    final response = await apiClient.get('/users/me');
    if (!response.containsKey('data') || response['data'] == null) {
      throw ApiException(
        code: 'MALFORMED',
        message: 'Missing expected "data" field in response.',
      );
    }
    return response['data'] as Map<String, dynamic>;
  }
}
