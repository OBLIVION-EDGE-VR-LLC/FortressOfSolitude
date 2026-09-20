# Software User Document: FortressOfSolitude

**Project Name:** FortressOfSolitude  
**Version:** 1.0  
**Original Development Period:** 2019 -- 2022  
**Framework:** Django 3.2.5 (Python 3.x)  
**Document Date:** September 2026  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation and Setup](#2-installation-and-setup)
3. [User Registration and Authentication](#3-user-registration-and-authentication)
4. [Blog Management](#4-blog-management)
5. [Encrypted Posts and Secure Notes](#5-encrypted-posts-and-secure-notes)
6. [Task and Project Management](#6-task-and-project-management)
7. [Encrypted File Management](#7-encrypted-file-management)
8. [Tags and Content Organization](#8-tags-and-content-organization)
9. [Startup and News Tracking](#9-startup-and-news-tracking)
10. [User Profile Management](#10-user-profile-management)
11. [System Architecture for Users](#11-system-architecture-for-users)
12. [Troubleshooting and FAQ](#12-troubleshooting-and-faq)

---

## 1. Introduction

### 1.1 What is FortressOfSolitude?

FortressOfSolitude is a personal data vault and content management system built with the Django web framework. Named after Superman's legendary Arctic refuge, the application serves as a secure, self-hosted platform for managing blog posts, encrypted notes, task tracking, and encrypted file storage. The core distinguishing feature of FortressOfSolitude is its two-tier encryption system, which encrypts your sensitive data at rest using industry-standard AES-256 encryption. This means that even if someone gains access to the server's database or file system, they cannot read your encrypted content without your password.

The application was designed for individuals who want full control over their data and its encryption. Unlike cloud-based services that manage encryption keys on your behalf, FortressOfSolitude derives encryption keys directly from your password, ensuring that you are the sole person who can decrypt your private content. The system supports multiple types of content: traditional blog posts for public or semi-public writing, encrypted notes for truly private content, task management for organizing projects, and encrypted file storage for images, music, videos, and other documents.

### 1.2 Key Features

FortressOfSolitude provides a comprehensive suite of features organized around content creation, organization, and security. The blogging system supports both plaintext and encrypted posts, with date-based archives and tag-based categorization. The encryption system uses a two-tier key architecture (KEK/DEK) with AES-256-EAX authenticated encryption, ensuring both confidentiality and integrity of your data. The task management system lets you track projects with assignees, priorities, statuses, and due dates. The file management system encrypts uploaded images, music, videos, and other files before storing them on disk, and decrypts them on-the-fly when you download them. The user system features email-based authentication with customizable profiles.

### 1.3 Who Should Use This Document

This document is intended for end users who will interact with the FortressOfSolitude web interface, system administrators who will install and maintain the application, and developers who want to understand the user-facing features before diving into the codebase. The document assumes basic familiarity with web applications, Python virtual environments, and command-line tools for the installation sections. The usage sections assume only web browser literacy.

---

## 2. Installation and Setup

### 2.1 Prerequisites

Before installing FortressOfSolitude, you will need several software components available on your system. Python 3.8 or later is required as the runtime environment; the project was developed with Python 3.8 and the virtual environment currently uses Python 3.12, so any version in that range should work. You will also need pip (Python's package manager), which typically comes bundled with Python installations. For the Celery-based asynchronous task processing features, you will need a message broker such as RabbitMQ or Redis installed and running. SQLite3 is used as the default database and is typically included with Python, so no separate database installation is needed for development use.

Additionally, Java must be installed if you wish to regenerate the architectural diagrams from the PlantUML source files in the `docs/diagrams/` directory. PlantUML is a Java-based tool that converts text-based diagram descriptions into PNG images. However, the pre-rendered PNG diagrams are included in the repository, so Java is only needed if you want to modify and re-render the diagrams.

### 2.2 Installation Steps

To install FortressOfSolitude, begin by cloning the repository to your local machine. Navigate to the project root directory, which contains the `manage.py` file, the `_FortressOfSolitude/` Django project directory, and the `requirements.txt` file. Create a Python virtual environment by running `python3 -m venv fortress`, which will create the virtual environment in the `fortress/` directory, matching the project's convention. Activate the virtual environment with `source fortress/bin/activate` on Linux/macOS or `fortress\Scripts\activate` on Windows.

With the virtual environment active, install the project dependencies by running `pip install -r requirements.txt`. This will install Django 3.2.5, PyCryptodome (for AES and RSA encryption), the cryptography library (for PBKDF2 key derivation), Pillow (for image processing), django-ckeditor (for rich text editing), and the Celery stack (for asynchronous task processing). After the dependencies are installed, you need to apply the database migrations to create the SQLite3 database schema. Run `python manage.py migrate` to apply all migrations across the Blog, Organizer, NeutrinoKey, Superhero, and Core apps. This creates the `db.sqlite3` file with all necessary tables.

### 2.3 Initial Configuration

Before running the application, you should review and update the settings in `_FortressOfSolitude/settings.py`. The most critical settings to update are the `SECRET_KEY` (replace the placeholder with a unique, randomly generated key), the `ALLOWED_HOSTS` list (add your server's hostname or IP address), and the `DAILY_PLANET_AES_DEK` (the shared encryption key for publicly viewable encrypted posts). For development use on your local machine, the default values of `["127.0.0.1", "localhost"]` for ALLOWED_HOSTS and `DEBUG = True` are appropriate. For any deployment accessible over a network, change `DEBUG` to `False` and configure the SSL-related settings.

To create an administrative superuser account, run `python manage.py createsuperuser`. You will be prompted for an email address and password (note that FortressOfSolitude uses email-based login, not usernames). This superuser account will have full access to the Django admin interface at `/admin/` and all application features.

### 2.4 Starting the Application

Start the development server by running `python manage.py runserver`. By default, this will serve the application at `http://127.0.0.1:8000/`. Open this URL in your web browser to access the FortressOfSolitude home page. If you want to use the Celery asynchronous task features, open a separate terminal, activate the virtual environment, and run `celery -A _FortressOfSolitude worker -l info` to start the Celery worker process. The worker will connect to your configured message broker and begin processing background tasks.

The application is now ready for use. Navigate to `http://127.0.0.1:8000/superhero/register/` to create your first user account, or log in with the superuser account you created earlier at `http://127.0.0.1:8000/superhero/login/`.

---

## 3. User Registration and Authentication

### 3.1 Creating an Account

New users register through the registration page at `/superhero/register/`. The registration form, themed as a "Daily Planet Subscriber" form, requires an email address and a password entered twice for confirmation. The email address serves as your login credential -- FortressOfSolitude does not use traditional usernames. Choose a strong password, as this password is not only used for login authentication but is also the root of your encryption key derivation chain. Your encrypted content is ultimately protected by the strength of this password; a weak password compromises the security of all your encrypted data, regardless of the strength of the underlying AES-256 encryption.

Upon successful registration, the system creates your user account and an associated profile, and assigns you to the "DailyPlanet_Writer" permission group. This default group grants permissions for creating and viewing blog posts, tasks, and tags. You will be redirected to a success page confirming your registration. From there, you can navigate to the login page to access the application.

The following diagram illustrates the complete authentication flow, from registration through login, accessing protected resources, and logout.

![Authentication Flow](diagrams/authentication_sequence.png)

### 3.2 Logging In

The login page is located at `/superhero/login/`. Enter the email address and password you used during registration. If authentication succeeds, you will be redirected to the task creation page, which serves as the application's primary landing page for authenticated users. If authentication fails, the login form will be re-displayed with an error message indicating invalid credentials.

Your login session is managed through Django's session framework. A session cookie is stored in your browser, keeping you logged in until you explicitly log out or the session expires. The session cookie is HTTP-only, preventing JavaScript-based session theft. During development, the session cookie is not marked as Secure (since development typically uses HTTP rather than HTTPS), but in a production deployment, the session cookie should be configured as Secure to ensure it is only transmitted over encrypted HTTPS connections.

### 3.3 Logging Out

To log out, navigate to `/superhero/logout/`. This destroys your server-side session and clears the session cookie from your browser. After logging out, you will be redirected to the login page. It is important to log out when you are finished using the application, especially on shared computers, because your session provides access to all your content-creation features and, if you have entered your encryption password during the session, decrypted content may be cached in your browser.

### 3.4 Permissions and Access Levels

FortressOfSolitude uses a permission-based access control system. The "DailyPlanet_Writer" default group provides permissions for standard content operations: creating and viewing blog posts, managing tasks and tags, and uploading files. Administrative operations (managing users, accessing the Django admin interface, deleting content created by other users) require staff or superuser status, which can be granted through the admin interface. The `view_future_post` permission controls whether you can see blog posts with publication dates in the future, which is useful for previewing scheduled content.

If you encounter a "403 Forbidden" error when accessing a page, it means your account lacks the required permission. Contact your system administrator to request the appropriate permission or group membership.

---

## 4. Blog Management

### 4.1 Creating Blog Posts

The blog post creation page is accessible at `/blog/create/`. This page presents a form with fields for the post title, slug (URL-friendly identifier), text content, publication date, and tag associations. The title should be descriptive and concise (maximum 63 characters). The slug is automatically generated from the title but can be customized; it forms part of the post's URL (e.g., `/blog/2022/03/my-first-post/`). The text field accepts plain text content for standard (unencrypted) blog posts.

When you submit the form, the post is saved to the database and becomes visible in the blog post list and date-based archives. If the publication date is in the future, the post will only be visible to users with the `view_future_post` permission until the publication date arrives. Posts can be associated with multiple tags for categorization and with multiple tasks for project management tracking.

### 4.2 Viewing and Navigating Posts

The blog post list is accessible at `/blog/` and displays all published posts in reverse chronological order. Each post shows its title, publication date, and associated tags. Clicking a post title takes you to the full post detail view at `/blog/YYYY/MM/slug/`, where YYYY is the four-digit year, MM is the two-digit month, and slug is the post's URL-friendly identifier.

The date-based archive system allows you to browse posts by year (`/blog/YYYY/`) or by year and month (`/blog/YYYY/MM/`). This hierarchical navigation is useful for finding older content or reviewing your posting history over time. Tags provide an alternative navigation axis: clicking a tag name shows all posts associated with that tag.

### 4.3 Editing and Deleting Posts

To edit an existing post, navigate to its detail page and access the update URL at `/blog/YYYY/MM/slug/update/`. The update form pre-populates with the post's current content, allowing you to modify the title, text, tags, or other fields. Saving the form updates the post in place without changing its URL or publication date (unless you explicitly modify those fields).

To delete a post, navigate to the delete URL at `/blog/YYYY/MM/slug/delete/`. You will be presented with a confirmation page before the post is permanently removed. Deletion is irreversible -- once a post is deleted, its content is removed from the database and cannot be recovered. For encrypted posts, the associated encryption keys (KEK/DEK) remain in the database but become orphaned, as they no longer reference any content.

---

## 5. Encrypted Posts and Secure Notes

### 5.1 Understanding Encryption in FortressOfSolitude

FortressOfSolitude provides two types of encrypted content: private encrypted posts and public encrypted posts. Both types encrypt the post content using AES-256-EAX authenticated encryption before storing it in the database. The critical difference lies in how the encryption keys are managed, which determines who can decrypt and read the content.

The system uses a two-tier encryption architecture illustrated in the diagram below. Your password is used to derive a Key Encryption Key (KEK), which in turn is used to derive a Data Encryption Key (DEK). The DEK encrypts your actual content. Both the KEK and DEK are stored in the database in wrapped (encrypted) form -- they can only be unwrapped by providing the correct password. This means that the database never contains plaintext keys or plaintext content.

![Encryption Architecture](diagrams/encryption_architecture.png)

Private encrypted posts use your personal password to derive the KEK/DEK chain. Only you (or someone who knows your password) can decrypt these posts. Public encrypted posts use a shared encryption key (the "Daily Planet" key) configured in the application settings. These posts are encrypted at rest in the database but can be decrypted by the application for display to any visitor. Public encryption protects against database theft while still allowing public readability through the web interface.

### 5.2 Creating Private Encrypted Posts

To create a private encrypted post, navigate to `/blog/Securecreate/`. The form is similar to the standard post creation form but includes a password field. Enter the content you want to encrypt in the text field, and provide your encryption password. This password can be the same as your login password or a different password dedicated to encryption; however, remember that you must provide this exact password to decrypt and view the post later.

When you submit the form, the Librarian encryption manager performs the following sequence: it derives a KEK from your password, derives a DEK from the KEK, encrypts your post text with AES-256-EAX using the DEK, stores the encrypted ciphertext (along with the encryption nonce and key references) in the database, and securely erases the raw key material from memory. The entire process happens server-side in a fraction of a second. You will be redirected to the secure post list upon success.

### 5.3 Viewing Private Encrypted Posts

The list of private encrypted posts is accessible at `/blog/Securelist/`. Each entry shows the post title and metadata, but the content is displayed in encrypted form (ciphertext). To view the decrypted content, you need to provide the password that was used during encryption. The Gor_El decryption manager reverses the encryption process: it unwraps the KEK using your password, unwraps the DEK using the KEK, decrypts the content using the DEK, and displays the plaintext. If you provide an incorrect password, the decryption will fail because the AES-EAX authentication tag will not verify, and you will see an error rather than garbage data. This authentication property is a security feature: it ensures that you are notified of a failed decryption rather than silently receiving corrupted output.

### 5.4 Creating and Viewing Public Encrypted Posts

Public encrypted posts are created at `/blog/PublicSecurecreate/` and listed at `/blog/PublicSecurelist/`. The creation form includes a rich text editor (CKEditor) for formatting content with headings, bold text, links, and other HTML elements. Unlike private encrypted posts, public posts do not require you to enter an encryption password -- they use the application-wide "Daily Planet" encryption key configured in settings.

Public encrypted posts provide encryption at rest without restricting access. The content is encrypted when stored in the database, protecting against database-level attacks, but the application decrypts it automatically when serving it to any visitor. This is useful for content that you want to publish openly but also want to protect against database breaches or unauthorized direct database access.

### 5.5 Important Notes on Encryption Passwords

Your encryption password is the foundation of your data security. The system does not store your encryption password anywhere -- it is used transiently during encryption and decryption operations and then discarded. This means that if you forget your encryption password, there is no recovery mechanism. Your encrypted data will be permanently inaccessible. The system cannot reset or recover encryption passwords because it never possesses them; it only stores the encrypted (wrapped) keys that were derived from your password.

For this reason, it is strongly recommended that you use a password manager to store your encryption passwords securely. If you use different encryption passwords for different posts, record each password along with the corresponding post title. Consider the trade-off: using your login password as your encryption password is convenient but means that a compromised login password exposes all your encrypted data. Using a separate, strong encryption password provides an additional layer of defense but requires careful password management.

---

## 6. Task and Project Management

### 6.1 Creating Tasks

The task creation page is the default landing page for authenticated users, accessible at `/tasking/create/`. The task form includes fields for the task name, description, project codename, assignee, status, priority, and due date. The task name should be a concise, actionable description of the work item. The project codename groups related tasks together without requiring a formal project model. The assignee field tracks who is responsible for the task. Status and priority fields allow you to track task progression and importance.

Tasks can be associated with blog posts through a many-to-many relationship. This association is useful when blog posts serve as project documentation, research notes, or status updates related to specific tasks. You can link a task to multiple posts and a post to multiple tasks, creating a flexible network of relationships between your writing and your project management.

### 6.2 Viewing and Managing Tasks

Individual task details are accessible at `/tasking/slug/`, where slug is the URL-friendly version of the task name. The detail page displays all task fields, associated tags, and linked blog posts. You can update a task's fields (status, priority, assignee, etc.) through the update page at `/slug/update/`. The task list and detail views provide an overview of your project management state, helping you track what needs to be done, who is responsible, and what the current priorities are.

The task management system is intentionally lightweight compared to full-featured project management tools. It provides enough structure to organize personal or small-team work without the complexity of sprint planning, story points, or Kanban boards. The simplicity is by design: FortressOfSolitude is a personal data vault, and its task management focuses on tracking and accountability rather than process methodology.

---

## 7. Encrypted File Management

### 7.1 Uploading Encrypted Files

FortressOfSolitude encrypts uploaded files before storing them on disk, ensuring that even if an attacker gains filesystem access, the files are unreadable without the decryption password. The file upload page is accessible at `/upload/create/`. The upload form allows you to select a file, specify a name, and provide your encryption password. The system supports four file categories: images (photos), music files, video files, and miscellaneous files.

The following diagram illustrates the complete encrypted file upload and download workflow, showing how files are encrypted before storage and decrypted on retrieval.

![Encrypted File Upload and Download](diagrams/file_upload_sequence.png)

When you submit the upload form, the Librarian manager reads the file bytes into memory, derives a KEK from your password, derives a DEK from the KEK, encrypts the file bytes with AES-256-EAX using the DEK, writes the encrypted bytes to the appropriate storage directory on disk, saves the file metadata (name, path, nonce, key references) to the database, and securely erases the key material from memory. The raw file bytes are never written to disk -- only the encrypted ciphertext reaches the filesystem. This provides true encryption at rest for all uploaded files.

### 7.2 Downloading and Viewing Encrypted Files

Encrypted files can be accessed through the download pages. Images are available at `/download/`, music files at `/download/music/`, and miscellaneous files at `/download/misc/`. Individual files are retrieved through URLs like `/download/media/photos/{pk}`, where pk is the file's primary key in the database.

When you request a file download, the Gor_El decryption manager retrieves the encrypted file from disk, unwraps the KEK and DEK using your password, decrypts the file bytes with AES-256-EAX (verifying the authentication tag to ensure the file has not been tampered with), and returns the decrypted bytes as an HTTP response. Depending on the file type and your browser's configuration, the decrypted file will either be displayed inline (e.g., images) or offered as a download attachment. The decryption happens entirely in memory -- the decrypted file bytes are never written to disk on the server, ensuring that plaintext file content exists only transiently in server memory and in the data transmitted to your browser.

### 7.3 Supported File Types and Storage

Each file category has a dedicated storage directory on the server. Images are stored in the `media/photos/` directory, music in `media/music/`, videos in `media/videos/`, and miscellaneous files in `media/otherfiles/`. The files stored in these directories are encrypted ciphertext that appears as random binary data. There is no practical limit on file size beyond your server's available disk space and memory (since the file must fit in memory during encryption and decryption).

The system does not impose restrictions on file formats within each category. The "image" category can accept any image format (JPEG, PNG, GIF, BMP, etc.), the "music" category can accept any audio format (MP3, WAV, FLAC, OGG, etc.), and so on. The categorization is primarily organizational, affecting which storage directory is used and which download page lists the file. The encryption process treats all files as raw bytes regardless of format.

---

## 8. Tags and Content Organization

### 8.1 Creating and Managing Tags

Tags provide a flat categorization system for organizing content across the application. The tag creation page is accessible at `/tag/create/`. Each tag has a name (maximum 31 characters) and an automatically generated slug. Tags can be associated with blog posts (through the post creation and editing forms) and with startups (through the startup model's many-to-many relationship).

The tag list view at the root URL (`/`) displays all existing tags. Clicking a tag name navigates to the tag detail page at `/tag/slug/`, which shows all content associated with that tag, including blog posts and startups. Tags are intentionally simple -- they have no hierarchy, no descriptions, and no color coding. This simplicity keeps the organizational system lightweight and fast, suitable for personal use where a flat taxonomy is sufficient.

### 8.2 Using Tags Effectively

Tags work best when you establish consistent naming conventions. Consider using broad category tags (e.g., "security", "development", "personal") alongside specific topic tags (e.g., "encryption", "django", "project-alpha"). Applying multiple tags to a single post allows it to appear in multiple category views, making it discoverable through different navigation paths. Tags are shared across posts and startups, so using the same tag for related content across different content types creates useful cross-references.

---

## 9. Startup and News Tracking

### 9.1 Managing Startups

The startup tracking feature allows you to maintain a directory of startup companies with their basic information. Each startup record includes the company name, a description, founded date, contact email, website URL, and associated tags. Startups are accessible through the tag-based navigation system -- each startup is linked to tags, and viewing a tag's detail page shows the associated startups alongside blog posts.

Startups can have associated news links, which are articles or resources related to the company. Each news link includes a title, URL, publication date, and a foreign key relationship to the parent startup. This creates a simple knowledge base where you can track companies of interest along with relevant news coverage, all organized through the tag taxonomy.

### 9.2 Browsing Startup Information

The startup detail page displays all fields for a startup along with its associated news links and tags. From a startup's detail page, you can navigate to its news links, to its tags (which show related content), or back to the tag list. The startup and news link models do not currently support encryption, as they are designed for storing publicly available business information rather than sensitive personal data.

---

## 10. User Profile Management

### 10.1 Profile Overview

Each user account has an associated profile that stores display information. The profile includes fields for your name, an about/bio section, and a profile avatar image. Your profile slug is derived from your email address and is used in profile URLs. The profile is automatically created during registration with default values that you can customize afterward.

### 10.2 Updating Your Profile

Profile updates are handled through the profile management views in the Superhero app. You can update your display name, about text, and profile avatar. When you upload a new avatar image, the system automatically resizes it to fit within a 300x300 pixel bounding box using Pillow's thumbnail function, maintaining the original aspect ratio. This ensures consistent avatar dimensions across the application's user interface without requiring you to manually resize images before uploading. Avatar images are stored in the `media/profile_avatars/` directory and are not encrypted, as they are intended for public display.

---

## 11. System Architecture for Users

### 11.1 How Your Data is Organized

Understanding the system's architecture helps you make informed decisions about how to use its features. The FortressOfSolitude is organized into five interconnected modules, each handling a specific aspect of the application. The following diagram provides a high-level view of how these modules interact.

![System Architecture Overview](diagrams/system_architecture.png)

The Blog module handles all blog post functionality, including both plaintext and encrypted posts. The Organizer module manages tasks, tags, startups, news links, and encrypted file storage. The NeutrinoKey module provides the encryption engine that both Blog and Organizer rely on. The Superhero module handles your user account, login, and permissions. The Core module provides shared utilities used across the other modules. All modules share a single SQLite3 database and a set of media directories for file storage.

### 11.2 How Encryption Protects Your Data

The encryption system is designed to protect your data in a "data at rest" scenario -- meaning that the data is encrypted while it sits in the database or on the disk. When you interact with encrypted content through the web interface, the data is decrypted in the server's memory for the duration of your request and then the key material is erased. The decrypted content travels over the network to your browser (which is why HTTPS is recommended for production deployments) and is displayed in your browser window.

The two-tier key architecture means that your data is protected by two layers of encryption. Even if an attacker obtains both the database and the encrypted files on disk, they still need your password to unwrap the KEK, which is needed to unwrap the DEK, which is needed to decrypt the data. The AES-EAX authenticated encryption ensures that any attempt to tamper with the encrypted data will be detected during decryption, preventing sophisticated attacks that modify ciphertext to manipulate the decrypted output.

### 11.3 Deployment Overview

The following diagram shows the full deployment architecture of the FortressOfSolitude, including the application server, database, file storage, and supporting services.

![Deployment Architecture](diagrams/deployment.png)

The application runs within a Python virtual environment that contains all necessary libraries. The SQLite3 database stores all structured data (user accounts, posts, tasks, encryption keys). The media directories store encrypted binary files. The optional Celery worker handles asynchronous tasks through a message broker. For production use, the Django development server should be replaced with a production-grade WSGI server (such as Gunicorn) behind a reverse proxy (such as Nginx) with HTTPS enabled.

---

## 12. Troubleshooting and FAQ

### 12.1 Common Issues

**"I forgot my encryption password."** Unfortunately, there is no password recovery mechanism for encryption passwords. The system does not store your encryption password -- it only stores encrypted (wrapped) keys derived from your password. If you forget the password, the encrypted data associated with that password is permanently inaccessible. This is a fundamental property of the encryption design, not a limitation that can be patched. Use a password manager to avoid this situation.

**"I get a 403 Forbidden error when accessing a page."** This means your user account lacks the required permission. By default, new accounts are assigned to the "DailyPlanet_Writer" group, which provides standard content creation permissions. If you need additional permissions (such as access to administrative features or the ability to view future-dated posts), contact your system administrator or, if you are the administrator, assign the appropriate permissions through the Django admin interface at `/admin/`.

**"The server won't start -- 'address already in use'."** Another process is using port 8000. Either stop the other process or run the Django development server on a different port: `python manage.py runserver 8080`.

**"Decryption fails with an error about authentication tags."** This typically means you entered the wrong password. AES-EAX verifies an authentication tag during decryption; if the password (and therefore the derived keys) is wrong, the tag verification fails. Double-check your password and try again. If you are certain the password is correct, the encrypted data may have been corrupted in the database.

**"File upload is slow or times out."** Large files require more time for encryption because the entire file must be read into memory, encrypted, and written to disk. Consider breaking very large files into smaller pieces before uploading, or increasing your web server's request timeout setting. If you are using the Django development server, it has no explicit timeout, but reverse proxies (Nginx, Apache) typically do.

### 12.2 Security Best Practices

Maintaining the security of your FortressOfSolitude installation requires attention to both the application configuration and your personal practices. Keep the following guidelines in mind for secure operation of the system.

Use strong, unique passwords for both your login account and your encryption operations. A password manager like Bitwarden, 1Password, or KeePass can help you generate and store strong passwords without memorizing them. Enable HTTPS for any deployment accessible over a network to protect data in transit between your browser and the server. Keep the application and its dependencies updated to patch security vulnerabilities in Django, PyCryptodome, and other libraries. Regularly back up your SQLite3 database and media directories; while the backups will contain only encrypted data, they ensure you can recover from hardware failures or data corruption. Restrict filesystem permissions on the `db.sqlite3` file and media directories to prevent unauthorized local access.

### 12.3 Frequently Asked Questions

**Q: Can I change my encryption password after creating encrypted posts?**  
A: The current implementation derives encryption keys from the password provided at the time of encryption. Changing your login password does not re-encrypt existing content. To use a new encryption password, you would need to decrypt existing content with the old password and re-encrypt it with the new password. The NeutronCore model supports multiple KEKs per user to facilitate key rotation, but the automated key rotation workflow is not currently exposed through the web interface.

**Q: Is my data safe if someone steals the server?**  
A: Yes, for encrypted content. All encrypted posts and files are stored as ciphertext that is computationally infeasible to decrypt without your password. Unencrypted blog posts, tasks, tags, and startup information would be accessible to anyone with database access. Profile information (including avatar images) is also stored in plaintext.

**Q: Can multiple users share encrypted content?**  
A: Private encrypted posts are tied to a single user's password. To share encrypted content, you would need to share the encryption password with the other user, which has obvious security implications. Public encrypted posts (using the "Daily Planet" shared key) are viewable by all visitors and represent the application's built-in sharing mechanism.

**Q: What happens if the database is corrupted?**  
A: If the database is corrupted, you may lose access to both your encrypted content and the encryption keys stored in the database. Even if you have your password, you need the wrapped KEK and DEK records from the database to decrypt your content. Regular database backups are essential.

**Q: Can I migrate from SQLite3 to PostgreSQL?**  
A: Yes. The application uses Django's ORM and a database router (KryptonianSpeak), which abstract the database backend. To migrate, update the DATABASES setting in `settings.py` to point to a PostgreSQL database, run `python manage.py migrate` to create the schema, and use Django's `dumpdata` and `loaddata` management commands to transfer existing data.

---

*This document describes the user-facing features and operational procedures for the FortressOfSolitude application as designed and implemented between 2019 and 2022.*
