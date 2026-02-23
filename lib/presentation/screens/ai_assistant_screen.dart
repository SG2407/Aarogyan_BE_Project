import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/chat_provider.dart';
import '../../data/models/chat_message.dart';

class ChatMessage {
  final String sender; // 'user' or 'ai'
  final String content;
  final DateTime createdAt;

  ChatMessage({
    required this.sender,
    required this.content,
    required this.createdAt,
  });
}

class AiAssistantScreen extends ConsumerStatefulWidget {
  const AiAssistantScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<AiAssistantScreen> createState() => _AiAssistantScreenState();
}

class _AiAssistantScreenState extends ConsumerState<AiAssistantScreen> {
  final TextEditingController _controller = TextEditingController();
  String? _chatId;
  List<ChatMessageModel> _messages = [];
  bool _isLoading = false;
  bool _initLoading = true;

  @override
  void initState() {
    super.initState();
    _startNewChat();
  }

  Future<void> _startNewChat() async {
    setState(() {
      _initLoading = true;
      _messages = [];
    });
    final repo = ref.read(chatRepositoryProvider);
    final chatId = await repo.createChat();
    setState(() {
      _chatId = chatId;
      _initLoading = false;
    });
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _chatId == null) return;
    setState(() {
      _isLoading = true;
      _controller.clear();
    });
    final repo = ref.read(chatRepositoryProvider);
    try {
      await repo.sendMessage(_chatId!, text);
      // Wait a short moment to ensure AI message is stored
      await Future.delayed(const Duration(milliseconds: 600));
      final msgs = await repo.fetchMessages(_chatId!);
      // Debug print
      // ignore: avoid_print
      print('Fetched messages after send:');
      for (final m in msgs) {
        print('  ${m.sender}: ${m.content}');
      }
      // Ensure AI message is present
      final hasAi = msgs.any((m) => m.sender == 'ai');
      if (!hasAi) {
        // Try again after a short delay
        await Future.delayed(const Duration(seconds: 1));
        final msgs2 = await repo.fetchMessages(_chatId!);
        print('Fetched messages after retry:');
        for (final m in msgs2) {
          print('  ${m.sender}: ${m.content}');
        }
        setState(() {
          _messages = msgs2;
          _isLoading = false;
        });
      } else {
        setState(() {
          _messages = msgs;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Failed to send message: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Medical Assistant'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'New Chat',
            onPressed: _isLoading ? null : _startNewChat,
          ),
        ],
      ),
      body: _initLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    reverse: true,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final msg = _messages[_messages.length - 1 - index];
                      final isUser = msg.sender == 'user';
                      return Align(
                        alignment: isUser
                            ? Alignment.centerRight
                            : Alignment.centerLeft,
                        child: Container(
                          margin: const EdgeInsets.symmetric(vertical: 4),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: isUser
                                ? Theme.of(
                                    context,
                                  ).colorScheme.primary.withOpacity(0.2)
                                : Colors.grey[200],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: isUser
                                ? CrossAxisAlignment.end
                                : CrossAxisAlignment.start,
                            children: [
                              Text(
                                isUser ? 'You' : 'AI',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: isUser
                                      ? Theme.of(context).colorScheme.primary
                                      : Colors.black54,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(msg.content),
                              const SizedBox(height: 2),
                              Text(
                                _formatTime(msg.createdAt),
                                style: const TextStyle(
                                  fontSize: 10,
                                  color: Colors.grey,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                if (_isLoading)
                  const Padding(
                    padding: EdgeInsets.all(8.0),
                    child: CircularProgressIndicator(),
                  ),
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _controller,
                          decoration: const InputDecoration(
                            hintText: 'Type your medical question...',
                            border: OutlineInputBorder(),
                          ),
                          onSubmitted: (_) => _sendMessage(),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.send),
                        onPressed: _isLoading ? null : _sendMessage,
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  String _formatTime(DateTime dt) {
    final hour = dt.hour.toString().padLeft(2, '0');
    final min = dt.minute.toString().padLeft(2, '0');
    return '$hour:$min';
  }
}
