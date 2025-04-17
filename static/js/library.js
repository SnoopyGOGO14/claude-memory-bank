// Library Agent Interface JavaScript
// Controls UI interactions and API calls for the Library Agent

// Debug mode for extra logging
const DEBUG = true;

// Logger utility
const Logger = {
    info: function(message) {
        const timestamp = new Date().toISOString();
        console.info(`[${timestamp}] [INFO] ${message}`);
        this.logToUI('info', message);
    },
    
    error: function(message, error) {
        const timestamp = new Date().toISOString();
        console.error(`[${timestamp}] [ERROR] ${message}`, error);
        this.logToUI('error', message);
    },
    
    debug: function(message, data) {
        if (DEBUG) {
            const timestamp = new Date().toISOString();
            console.debug(`[${timestamp}] [DEBUG] ${message}`, data);
        }
    },
    
    warn: function(message) {
        const timestamp = new Date().toISOString();
        console.warn(`[${timestamp}] [WARN] ${message}`);
        this.logToUI('warning', message);
    },
    
    logToUI: function(level, message) {
        const statusPanel = document.getElementById('status-messages');
        if (statusPanel) {
            const logEntry = document.createElement('div');
            logEntry.className = `status-entry status-${level}`;
            logEntry.innerHTML = `<span class="status-time">${new Date().toLocaleTimeString()}</span> <span class="status-message">${message}</span>`;
            statusPanel.prepend(logEntry);
            
            // Limit to 10 latest messages
            const maxMessages = 10;
            const entries = statusPanel.querySelectorAll('.status-entry');
            if (entries.length > maxMessages) {
                for (let i = maxMessages; i < entries.length; i++) {
                    statusPanel.removeChild(entries[i]);
                }
            }
        }
    }
};

// API utility functions
const API = {
    // Scan a directory for documents
    scanDirectory: async function(directory, includeSubfolders = false) {
        Logger.info(`Scanning directory: ${directory}`);
        try {
            Logger.debug('API call: /api/library/scan', { directory, recursive: includeSubfolders });
            
            const response = await fetch('/api/library/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    directory: directory,
                    recursive: includeSubfolders
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            Logger.debug('API response: /api/library/scan', data);
            
            if (data.status === 'success') {
                Logger.info(`Scan completed. Found ${data.result.count} documents.`);
                return data.result;
            } else {
                Logger.error(`Scan failed: ${data.message}`, null);
                return null;
            }
        } catch (error) {
            Logger.error('Error scanning directory', error);
            throw error;
        }
    },
    
    // Search for documents
    searchDocuments: async function(query, limit = 10) {
        Logger.info(`Searching for: ${query}`);
        try {
            Logger.debug('API call: /api/library/search', { query, limit });
            
            const response = await fetch('/api/library/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    limit: limit
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            Logger.debug('API response: /api/library/search', data);
            
            if (data.status === 'success') {
                Logger.info(`Search completed. Found ${data.result.length} results.`);
                return data.result;
            } else {
                Logger.error(`Search failed: ${data.message}`, null);
                return [];
            }
        } catch (error) {
            Logger.error('Error searching documents', error);
            return [];
        }
    },
    
    // Get library statistics
    getStats: async function() {
        Logger.info('Fetching library statistics');
        try {
            Logger.debug('API call: /api/library/stats');
            
            const response = await fetch('/api/library/stats', {
                method: 'GET'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            Logger.debug('API response: /api/library/stats', data);
            
            if (data.status === 'success') {
                Logger.info('Statistics retrieved successfully');
                return data.result;
            } else {
                Logger.error(`Failed to get statistics: ${data.message}`, null);
                return null;
            }
        } catch (error) {
            Logger.error('Error fetching statistics', error);
            return null;
        }
    },
    
    // Upload files
    uploadFiles: async function(formData) {
        Logger.info('Uploading files');
        try {
            Logger.debug('API call: /api/library/upload');
            
            const response = await fetch('/api/library/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            Logger.debug('API response: /api/library/upload', data);
            
            if (data.status === 'success') {
                Logger.info(`Upload completed. Processed ${data.result.count} files.`);
                return data.result;
            } else {
                Logger.error(`Upload failed: ${data.message}`, null);
                return null;
            }
        } catch (error) {
            Logger.error('Error uploading files', error);
            throw error;
        }
    },
    
    // Open a document
    openDocument: async function(filename) {
        Logger.info(`Opening document: ${filename}`);
        try {
            Logger.debug('API call: /api/library/open', { filename });
            
            const response = await fetch('/api/library/open', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: filename
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            Logger.debug('API response: /api/library/open', data);
            
            if (data.status === 'success') {
                Logger.info(`Opening document: ${filename}`);
                return data;
            } else {
                Logger.error(`Failed to open document: ${data.message}`, null);
                return null;
            }
        } catch (error) {
            Logger.error('Error opening document', error);
            return null;
        }
    }
};

// UI Controllers
const UI = {
    init: function() {
        Logger.info('Initializing Library UI');
        this.attachEventListeners();
        this.refreshStats();
        
        // Set up drag and drop for file upload
        this.setupDragAndDrop();
    },
    
    attachEventListeners: function() {
        Logger.debug('Attaching event listeners to UI elements');
        
        // Scan button
        document.getElementById('btn-scan').addEventListener('click', function() {
            Logger.debug('Scan button clicked');
            const directory = document.getElementById('scan-directory').value;
            const includeSubfolders = document.getElementById('include-subfolders').checked;
            
            if (!directory || directory.trim() === '') {
                Logger.warn('No directory specified for scanning');
                return;
            }
            
            UI.showLoading('Scanning directory...');
            
            API.scanDirectory(directory, includeSubfolders)
                .then(result => {
                    if (result) {
                        UI.hideLoading();
                        UI.showDocuments(result.documents);
                        UI.refreshStats();
                    } else {
                        UI.hideLoading();
                        UI.showError('Scan failed. Check the logs for details.');
                    }
                })
                .catch(error => {
                    UI.hideLoading();
                    UI.showError('Error scanning directory: ' + error.message);
                });
        });
        
        // Scan default folder button
        document.getElementById('btn-scan-default').addEventListener('click', function() {
            Logger.debug('Scan default folder button clicked');
            UI.showLoading('Scanning default folder...');
            
            API.scanDirectory('/Volumes/1TB Kingston Sata/Sovereign AI/CLAUDE_MEMORY_BANK', true)
                .then(result => {
                    if (result) {
                        UI.hideLoading();
                        UI.showDocuments(result.documents);
                        UI.refreshStats();
                    } else {
                        UI.hideLoading();
                        UI.showError('Default scan failed. Check the logs for details.');
                    }
                })
                .catch(error => {
                    UI.hideLoading();
                    UI.showError('Error scanning default directory: ' + error.message);
                });
        });
        
        // Search button
        document.getElementById('btn-search').addEventListener('click', function() {
            Logger.debug('Search button clicked');
            const query = document.getElementById('search-query').value;
            
            if (!query || query.trim() === '') {
                Logger.warn('No search query specified');
                return;
            }
            
            UI.showLoading('Searching...');
            
            API.searchDocuments(query)
                .then(results => {
                    UI.hideLoading();
                    UI.showSearchResults(results);
                })
                .catch(error => {
                    UI.hideLoading();
                    UI.showError('Error searching: ' + error.message);
                });
        });
        
        // File select button
        document.getElementById('btn-file-select').addEventListener('click', function() {
            Logger.debug('File select button clicked');
            document.getElementById('file-upload').click();
        });
        
        // File upload change event
        document.getElementById('file-upload').addEventListener('change', function(e) {
            Logger.debug('Files selected for upload', e.target.files);
            if (e.target.files.length > 0) {
                UI.uploadFiles(e.target.files);
            }
        });
        
        // Refresh stats button
        document.getElementById('btn-refresh-stats').addEventListener('click', function() {
            Logger.debug('Refresh stats button clicked');
            UI.refreshStats();
        });
        
        // Organization filter change
        document.getElementById('organization-filter').addEventListener('change', function() {
            Logger.debug('Organization filter changed to: ' + this.value);
            UI.applyFilters();
        });
        
        // File type filter change
        document.getElementById('filetype-filter').addEventListener('change', function() {
            Logger.debug('File type filter changed to: ' + this.value);
            UI.applyFilters();
        });
    },
    
    setupDragAndDrop: function() {
        const dropZone = document.getElementById('drop-zone');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, function(e) {
                e.preventDefault();
                e.stopPropagation();
                Logger.debug(`Drag event: ${eventName}`);
            }, false);
        });
        
        dropZone.addEventListener('dragenter', function() {
            Logger.debug('File drag entered drop zone');
            dropZone.classList.add('drag-active');
        });
        
        dropZone.addEventListener('dragleave', function() {
            Logger.debug('File drag left drop zone');
            dropZone.classList.remove('drag-active');
        });
        
        dropZone.addEventListener('drop', function(e) {
            Logger.debug('Files dropped in drop zone', e.dataTransfer.files);
            dropZone.classList.remove('drag-active');
            if (e.dataTransfer.files.length > 0) {
                UI.uploadFiles(e.dataTransfer.files);
            }
        });
    },
    
    uploadFiles: function(files) {
        Logger.info(`Uploading ${files.length} files`);
        
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
            Logger.debug(`Adding file to upload: ${file.name} (${file.size} bytes)`);
        });
        
        UI.showLoading('Uploading files...');
        
        API.uploadFiles(formData)
            .then(result => {
                if (result) {
                    UI.hideLoading();
                    UI.showSuccess(`Uploaded ${result.count} files successfully.`);
                    
                    // Show the newly uploaded documents
                    if (result.documents && result.documents.length > 0) {
                        UI.showDocuments(result.documents);
                    }
                    
                    // Refresh statistics
                    UI.refreshStats();
                } else {
                    UI.hideLoading();
                    UI.showError('Upload failed. Check the logs for details.');
                }
            })
            .catch(error => {
                UI.hideLoading();
                UI.showError('Error uploading files: ' + error.message);
            });
    },
    
    refreshStats: function() {
        Logger.info('Refreshing library statistics');
        
        UI.showStatsLoading();
        
        API.getStats()
            .then(stats => {
                if (stats) {
                    UI.updateStatsDisplay(stats);
                    
                    // Update organization filter options
                    if (stats.organizations && stats.organizations.length > 0) {
                        UI.updateOrganizationFilter(stats.organizations);
                    }
                    
                    // Update file type filter options
                    if (stats.file_types && stats.file_types.length > 0) {
                        UI.updateFileTypeFilter(stats.file_types);
                    }
                } else {
                    UI.showStatsError('Failed to load statistics');
                }
            })
            .catch(error => {
                UI.showStatsError('Error: ' + error.message);
            });
    },
    
    updateStatsDisplay: function(stats) {
        Logger.debug('Updating stats display', stats);
        
        const statsContainer = document.getElementById('stats-container');
        const statsData = document.createElement('div');
        statsData.className = 'stats-data';
        
        // Main stats
        statsData.innerHTML = `
            <div class="stat-box">
                <div class="stat-value">${stats.total_documents || 0}</div>
                <div class="stat-label">Documents</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${stats.organizations ? stats.organizations.length : 0}</div>
                <div class="stat-label">Organizations</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${stats.file_types ? stats.file_types.length : 0}</div>
                <div class="stat-label">File Types</div>
            </div>
        `;
        
        // Create category breakdown if available
        if (stats.categories && Object.keys(stats.categories).length > 0) {
            const categoriesSection = document.createElement('div');
            categoriesSection.className = 'categories-section';
            categoriesSection.innerHTML = '<h3>Categories</h3>';
            
            const categoriesList = document.createElement('div');
            categoriesList.className = 'categories-list';
            
            // Sort categories by count (descending)
            const sortedCategories = Object.entries(stats.categories)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5); // Show top 5
            
            sortedCategories.forEach(([category, count]) => {
                const categoryItem = document.createElement('div');
                categoryItem.className = 'category-item';
                categoryItem.innerHTML = `
                    <span class="category-name">${category}</span>
                    <span class="category-count">${count}</span>
                `;
                categoriesList.appendChild(categoryItem);
            });
            
            categoriesSection.appendChild(categoriesList);
            statsContainer.appendChild(categoriesSection);
        }
        
        // Display last updated time if available
        if (stats.last_updated) {
            const lastUpdated = document.createElement('div');
            lastUpdated.className = 'last-updated';
            
            // Format the date
            let date;
            try {
                date = new Date(stats.last_updated);
                lastUpdated.textContent = `Last updated: ${date.toLocaleString()}`;
            } catch (e) {
                lastUpdated.textContent = `Last updated: ${stats.last_updated}`;
            }
            
            statsContainer.appendChild(lastUpdated);
        }
        
        statsContainer.innerHTML = '';
        statsContainer.appendChild(statsData);
        
        Logger.info(`Statistics updated: ${stats.total_documents || 0} documents`);
    },
    
    updateOrganizationFilter: function(organizations) {
        Logger.debug('Updating organization filter options', organizations);
        
        const select = document.getElementById('organization-filter');
        const currentValue = select.value;
        
        select.innerHTML = '<option value="All">All Organizations</option>';
        
        if (organizations && organizations.length > 0) {
            organizations.forEach(org => {
                const option = document.createElement('option');
                option.value = org;
                option.textContent = org || 'Uncategorized';
                select.appendChild(option);
            });
        }
        
        // Restore previously selected value if it still exists
        if (currentValue && organizations && organizations.includes(currentValue)) {
            select.value = currentValue;
        }
    },
    
    updateFileTypeFilter: function(fileTypes) {
        Logger.debug('Updating file type filter options', fileTypes);
        
        const select = document.getElementById('filetype-filter');
        const currentValue = select.value;
        
        select.innerHTML = '<option value="All">All File Types</option>';
        
        if (fileTypes && fileTypes.length > 0) {
            fileTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = (type || 'Unknown').toUpperCase();
                select.appendChild(option);
            });
        }
        
        // Restore previously selected value if it still exists
        if (currentValue && fileTypes && fileTypes.includes(currentValue)) {
            select.value = currentValue;
        }
    },
    
    showDocuments: function(documents) {
        Logger.debug('Displaying documents', documents);
        
        const container = document.getElementById('document-container');
        
        // Store the documents in a global variable for filtering
        window.libraryDocuments = documents;
        
        // Display the documents
        this.renderDocuments(documents);
        
        // Update document count
        document.getElementById('results-count').textContent = `${documents.length} documents`;
    },
    
    renderDocuments: function(documents) {
        Logger.debug(`Rendering ${documents.length} documents`);
        
        const container = document.getElementById('document-container');
        container.innerHTML = '';
        
        if (documents.length === 0) {
            container.innerHTML = '<div class="empty-message">No documents found</div>';
            return;
        }
        
        const table = document.createElement('table');
        table.className = 'document-table';
        
        // Create table header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Filename</th>
                <th>Category</th>
                <th>Organization</th>
                <th>Type</th>
                <th>Actions</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        
        documents.forEach(doc => {
            const tr = document.createElement('tr');
            
            // Extract category from classification
            let category = 'Unknown';
            let summary = '';
            
            if (doc.classification) {
                try {
                    // Try to parse as JSON first
                    if (typeof doc.classification === 'string') {
                        try {
                            const classData = JSON.parse(doc.classification);
                            category = classData.category || classData.Category || 'Unknown';
                            summary = classData.summary || classData.Summary || '';
                        } catch (e) {
                            // If not JSON, try to extract first word as category
                            const words = doc.classification.split(' ');
                            if (words.length > 0) {
                                category = words[0];
                                summary = doc.classification;
                            }
                        }
                    } else if (typeof doc.classification === 'object') {
                        // Already an object
                        category = doc.classification.category || doc.classification.Category || 'Unknown';
                        summary = doc.classification.summary || doc.classification.Summary || '';
                    }
                } catch (e) {
                    Logger.error(`Error parsing classification for ${doc.filename}`, e);
                }
            }
            
            tr.innerHTML = `
                <td title="${doc.file_path}">${doc.filename || 'Unknown'}</td>
                <td title="${summary}">${category}</td>
                <td>${doc.organization || 'Unknown'}</td>
                <td>${doc.file_type || 'Unknown'}</td>
                <td>
                    <button class="btn-action btn-open" data-filename="${doc.filename}">Open</button>
                </td>
            `;
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        container.appendChild(table);
        
        // Add event listeners to the open buttons
        const openButtons = container.querySelectorAll('.btn-open');
        openButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filename = this.getAttribute('data-filename');
                Logger.debug(`Open button clicked for document: ${filename}`);
                
                UI.openDocument(filename);
            });
        });
        
        Logger.info(`Rendered ${documents.length} documents in table`);
    },
    
    openDocument: function(filename) {
        Logger.info(`Opening document: ${filename}`);
        
        UI.showLoading(`Opening ${filename}...`);
        
        API.openDocument(filename)
            .then(result => {
                UI.hideLoading();
                if (result) {
                    Logger.info(`Document opened successfully: ${filename}`);
                } else {
                    UI.showError(`Failed to open document: ${filename}`);
                }
            })
            .catch(error => {
                UI.hideLoading();
                UI.showError(`Error opening document: ${error.message}`);
            });
    },
    
    showSearchResults: function(results) {
        Logger.debug(`Displaying ${results.length} search results`);
        
        // Update the documents display with search results
        this.showDocuments(results);
        
        Logger.info(`Search returned ${results.length} results`);
    },
    
    applyFilters: function() {
        Logger.info('Applying document filters');
        
        const orgFilter = document.getElementById('organization-filter').value;
        const typeFilter = document.getElementById('filetype-filter').value;
        
        Logger.debug(`Filter values - Organization: ${orgFilter}, Type: ${typeFilter}`);
        
        // Make sure we have documents to filter
        if (!window.libraryDocuments) {
            Logger.warn('No documents available to filter');
            return;
        }
        
        let filtered = window.libraryDocuments;
        
        // Apply organization filter
        if (orgFilter !== 'All') {
            Logger.debug(`Filtering by organization: ${orgFilter}`);
            filtered = filtered.filter(doc => doc.organization === orgFilter);
        }
        
        // Apply file type filter
        if (typeFilter !== 'All') {
            Logger.debug(`Filtering by file type: ${typeFilter}`);
            filtered = filtered.filter(doc => doc.file_type === typeFilter);
        }
        
        // Update document count and render filtered documents
        document.getElementById('results-count').textContent = `${filtered.length} documents`;
        this.renderDocuments(filtered);
        
        Logger.info(`Applied filters. Showing ${filtered.length} documents`);
    },
    
    showLoading: function(message = 'Loading...') {
        Logger.debug(`Showing loading indicator: ${message}`);
        
        const loadingEl = document.getElementById('loading');
        loadingEl.textContent = message;
        loadingEl.style.display = 'block';
    },
    
    hideLoading: function() {
        Logger.debug('Hiding loading indicator');
        
        const loadingEl = document.getElementById('loading');
        loadingEl.style.display = 'none';
    },
    
    showStatsLoading: function() {
        Logger.debug('Showing stats loading indicator');
        
        const statsContainer = document.getElementById('stats-container');
        statsContainer.innerHTML = '<div class="stats-loading"><div class="spinner"></div></div>';
    },
    
    showStatsError: function(message) {
        Logger.error(`Stats error: ${message}`);
        
        const statsContainer = document.getElementById('stats-container');
        statsContainer.innerHTML = `<div class="stats-error">${message}</div>`;
    },
    
    showError: function(message) {
        Logger.error(`UI error: ${message}`);
        
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <span class="notification-close">&times;</span>
        `;
        
        document.body.appendChild(notification);
        
        // Add close button event
        notification.querySelector('.notification-close').addEventListener('click', function() {
            notification.remove();
        });
        
        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.remove();
            }
        }, 8000);
    },
    
    showSuccess: function(message) {
        Logger.info(`Success message: ${message}`);
        
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <span class="notification-close">&times;</span>
        `;
        
        document.body.appendChild(notification);
        
        // Add close button event
        notification.querySelector('.notification-close').addEventListener('click', function() {
            notification.remove();
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.remove();
            }
        }, 5000);
    }
};

// Initialize the UI when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    Logger.info('DOM loaded. Initializing Library Agent interface');
    UI.init();
}); 