import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../../../data/services/document_service.dart';
import 'dart:async';

class DocumentDigitizingScreen extends StatefulWidget {
  const DocumentDigitizingScreen({Key? key}) : super(key: key);

  @override
  State<DocumentDigitizingScreen> createState() =>
      _DocumentDigitizingScreenState();
}

class _DocumentDigitizingScreenState extends State<DocumentDigitizingScreen> {
  String? _selectedFileName;
  String? _selectedFilePath;
  bool _isUploading = false;
  String? _uploadStatus;

  List<dynamic> _documents = [];
  Map<String, dynamic>? _selectedDocument;
  String? _explanation;
  bool _isLoadingDocs = false;
  bool _isDeleting = false;

  @override
  void initState() {
    super.initState();
    _fetchDocuments();
  }

  Future<void> _fetchDocuments() async {
    setState(() => _isLoadingDocs = true);
    try {
      final docs = await DocumentService().listDocuments();
      setState(() {
        _documents = docs;
        _isLoadingDocs = false;
      });
    } catch (e) {
      setState(() => _isLoadingDocs = false);
    }
  }

  Future<void> _selectDocument(dynamic doc) async {
    setState(() {
      _selectedDocument = doc;
      _explanation = doc['explanation'] ?? '';
    });
  }

  Future<void> _deleteDocument(String docId) async {
    setState(() => _isDeleting = true);
    try {
      await DocumentService().deleteDocument(docId);
      setState(() {
        _documents.removeWhere((d) => d['id'] == docId);
        if (_selectedDocument != null && _selectedDocument!['id'] == docId) {
          _selectedDocument = null;
          _explanation = null;
        }
        _isDeleting = false;
      });
    } catch (e) {
      setState(() => _isDeleting = false);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Failed to delete document: $e')));
    }
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
    );
    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFileName = result.files.single.name;
        _selectedFilePath = result.files.single.path;
        _uploadStatus = null;
      });
    }
  }

  Future<void> _uploadFile() async {
    if (_selectedFilePath == null || _selectedFileName == null) return;
    setState(() {
      _isUploading = true;
      _uploadStatus = null;
    });
    try {
      // TODO: Replace with actual userId from auth provider
      const userId = 'demo-user';
      final result = await DocumentService().uploadDocument(
        filePath: _selectedFilePath!,
        fileName: _selectedFileName!,
        userId: userId,
      );
      setState(() {
        _uploadStatus = 'Upload successful!';
        _isUploading = false;
        _explanation = result['explanation'] ?? '';
      });
      _fetchDocuments();
    } catch (e) {
      setState(() {
        _uploadStatus = 'Upload failed: $e';
        _isUploading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Document Digitizing')),
      drawer: Drawer(
        child: SafeArea(
          child: _isLoadingDocs
              ? const Center(child: CircularProgressIndicator())
              : ListView(
                  children: [
                    const DrawerHeader(
                      child: Text(
                        'Your Documents',
                        style: TextStyle(fontSize: 20),
                      ),
                    ),
                    ..._documents.map(
                      (doc) => ListTile(
                        leading: const Icon(Icons.description),
                        title: Text(doc['file_name'] ?? 'Document'),
                        subtitle: Text(doc['created_at'] ?? ''),
                        selected:
                            _selectedDocument != null &&
                            _selectedDocument!['id'] == doc['id'],
                        onTap: () => _selectDocument(doc),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete, color: Colors.red),
                          onPressed: _isDeleting
                              ? null
                              : () => _deleteDocument(doc['id']),
                        ),
                      ),
                    ),
                  ],
                ),
        ),
      ),
      body: Center(
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.document_scanner, size: 80, color: Colors.blue),
              const SizedBox(height: 24),
              const Text(
                'Upload and digitize your medical documents!',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                icon: const Icon(Icons.upload_file),
                label: const Text('Select Document'),
                onPressed: _isUploading ? null : _pickFile,
              ),
              if (_selectedFileName != null) ...[
                const SizedBox(height: 12),
                Text('Selected: $_selectedFileName'),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: _isUploading ? null : _uploadFile,
                  child: _isUploading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Upload'),
                ),
              ],
              if (_uploadStatus != null) ...[
                const SizedBox(height: 12),
                Text(_uploadStatus!, style: TextStyle(color: Colors.green)),
              ],
              const SizedBox(height: 24),
              if (_explanation != null && _explanation!.isNotEmpty) ...[
                const Text(
                  'Explanation:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.symmetric(horizontal: 24),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(_explanation!),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
