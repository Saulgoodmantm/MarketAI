"""
LolzTeam API Client - Integration with LolzTeam Forum API
Documentation: https://lolzteam.readme.io/reference/information
"""

from typing import Dict, Any, Optional, List
from .base import BaseAPIClient


class LolzTeamAPI(BaseAPIClient):
    """
    Client for the LolzTeam Forum API.
    Provides access to forum data, user profiles, threads, and posts.
    """
    
    BASE_URL = "https://api.lolz.guru"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LolzTeam API client.
        
        Args:
            api_key: LolzTeam API key
        """
        super().__init__(api_key=api_key, base_url=self.BASE_URL)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with Bearer token authentication."""
        headers = super()._get_headers()
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    # === User Profile ===
    
    def get_me(self) -> Dict[str, Any]:
        """
        Get current user profile information.
        
        Returns:
            User profile data
        """
        return self.get('/users/me')
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get a specific user's profile.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data
        """
        return self.get(f'/users/{user_id}')
    
    def find_user(self, username: str) -> Dict[str, Any]:
        """
        Find a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User profile data
        """
        return self.get('/users/find', params={'username': username})
    
    def get_user_followers(self, user_id: int, page: int = 1) -> Dict[str, Any]:
        """
        Get a user's followers.
        
        Args:
            user_id: User ID
            page: Page number
            
        Returns:
            List of followers
        """
        return self.get(f'/users/{user_id}/followers', params={'page': page})
    
    def get_user_followings(self, user_id: int, page: int = 1) -> Dict[str, Any]:
        """
        Get users that a user is following.
        
        Args:
            user_id: User ID
            page: Page number
            
        Returns:
            List of followings
        """
        return self.get(f'/users/{user_id}/followings', params={'page': page})
    
    # === Forums ===
    
    def get_forums(self) -> Dict[str, Any]:
        """
        Get all available forums.
        
        Returns:
            List of forums
        """
        return self.get('/forums')
    
    def get_forum(self, forum_id: int) -> Dict[str, Any]:
        """
        Get a specific forum.
        
        Args:
            forum_id: Forum ID
            
        Returns:
            Forum data
        """
        return self.get(f'/forums/{forum_id}')
    
    def get_forum_followers(self, forum_id: int, page: int = 1) -> Dict[str, Any]:
        """
        Get followers of a forum.
        
        Args:
            forum_id: Forum ID
            page: Page number
            
        Returns:
            List of forum followers
        """
        return self.get(f'/forums/{forum_id}/followers', params={'page': page})
    
    # === Threads ===
    
    def get_threads(
        self,
        forum_id: Optional[int] = None,
        page: int = 1,
        order: str = 'last_post_date'
    ) -> Dict[str, Any]:
        """
        Get threads.
        
        Args:
            forum_id: Filter by forum ID
            page: Page number
            order: Sort order
            
        Returns:
            List of threads
        """
        params = {'page': page, 'order': order}
        if forum_id:
            params['forum_id'] = forum_id
        return self.get('/threads', params=params)
    
    def get_thread(self, thread_id: int) -> Dict[str, Any]:
        """
        Get a specific thread.
        
        Args:
            thread_id: Thread ID
            
        Returns:
            Thread data
        """
        return self.get(f'/threads/{thread_id}')
    
    def get_thread_posts(self, thread_id: int, page: int = 1) -> Dict[str, Any]:
        """
        Get posts in a thread.
        
        Args:
            thread_id: Thread ID
            page: Page number
            
        Returns:
            List of posts
        """
        return self.get(f'/threads/{thread_id}/posts', params={'page': page})
    
    def create_thread(
        self,
        forum_id: int,
        title: str,
        post_body: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new thread.
        
        Args:
            forum_id: Forum to post in
            title: Thread title
            post_body: Initial post content
            **kwargs: Additional options
            
        Returns:
            Created thread data
        """
        data = {
            'forum_id': forum_id,
            'thread_title': title,
            'post_body': post_body,
            **kwargs
        }
        return self.post('/threads', data=data)
    
    # === Posts ===
    
    def get_posts(self, page: int = 1) -> Dict[str, Any]:
        """
        Get recent posts.
        
        Args:
            page: Page number
            
        Returns:
            List of posts
        """
        return self.get('/posts', params={'page': page})
    
    def get_post(self, post_id: int) -> Dict[str, Any]:
        """
        Get a specific post.
        
        Args:
            post_id: Post ID
            
        Returns:
            Post data
        """
        return self.get(f'/posts/{post_id}')
    
    def create_post(self, thread_id: int, post_body: str) -> Dict[str, Any]:
        """
        Create a new post in a thread.
        
        Args:
            thread_id: Thread ID
            post_body: Post content
            
        Returns:
            Created post data
        """
        return self.post('/posts', data={
            'thread_id': thread_id,
            'post_body': post_body
        })
    
    def edit_post(self, post_id: int, post_body: str) -> Dict[str, Any]:
        """
        Edit an existing post.
        
        Args:
            post_id: Post ID
            post_body: New post content
            
        Returns:
            Updated post data
        """
        return self.put(f'/posts/{post_id}', data={'post_body': post_body})
    
    def delete_post(self, post_id: int) -> Dict[str, Any]:
        """
        Delete a post.
        
        Args:
            post_id: Post ID
            
        Returns:
            Deletion result
        """
        return self.delete(f'/posts/{post_id}')
    
    def like_post(self, post_id: int) -> Dict[str, Any]:
        """
        Like a post.
        
        Args:
            post_id: Post ID
            
        Returns:
            Like result
        """
        return self.post(f'/posts/{post_id}/likes')
    
    def unlike_post(self, post_id: int) -> Dict[str, Any]:
        """
        Remove like from a post.
        
        Args:
            post_id: Post ID
            
        Returns:
            Unlike result
        """
        return self.delete(f'/posts/{post_id}/likes')
    
    # === Conversations ===
    
    def get_conversations(self, page: int = 1) -> Dict[str, Any]:
        """
        Get user's conversations.
        
        Args:
            page: Page number
            
        Returns:
            List of conversations
        """
        return self.get('/conversations', params={'page': page})
    
    def get_conversation(self, conversation_id: int) -> Dict[str, Any]:
        """
        Get a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data
        """
        return self.get(f'/conversations/{conversation_id}')
    
    def create_conversation(
        self,
        recipients: str,
        title: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            recipients: Comma-separated user IDs
            title: Conversation title
            message: Initial message
            
        Returns:
            Created conversation data
        """
        return self.post('/conversations', data={
            'recipients': recipients,
            'conversation_title': title,
            'message_body': message
        })
    
    # === Notifications ===
    
    def get_notifications(self, page: int = 1) -> Dict[str, Any]:
        """
        Get user's notifications.
        
        Args:
            page: Page number
            
        Returns:
            List of notifications
        """
        return self.get('/notifications', params={'page': page})
    
    def mark_notifications_read(self) -> Dict[str, Any]:
        """
        Mark all notifications as read.
        
        Returns:
            Result
        """
        return self.post('/notifications/read')
    
    # === Search ===
    
    def search_threads(
        self,
        query: str,
        forum_id: Optional[int] = None,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search threads.
        
        Args:
            query: Search query
            forum_id: Filter by forum
            page: Page number
            
        Returns:
            Search results
        """
        params = {'q': query, 'page': page}
        if forum_id:
            params['forum_id'] = forum_id
        return self.get('/search/threads', params=params)
    
    def search_posts(
        self,
        query: str,
        user_id: Optional[int] = None,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search posts.
        
        Args:
            query: Search query
            user_id: Filter by user
            page: Page number
            
        Returns:
            Search results
        """
        params = {'q': query, 'page': page}
        if user_id:
            params['user_id'] = user_id
        return self.get('/search/posts', params=params)
    
    # === Utility Methods ===
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection and authentication.
        
        Returns:
            Connection test results
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'not_configured',
                'message': 'API key not set'
            }
        
        result = self.get_me()
        if result.get('success'):
            result['message'] = 'Connection successful'
        return result
    
    def get_forum_stats(self) -> Dict[str, Any]:
        """
        Get aggregated forum statistics.
        
        Returns:
            Forum statistics for AI learning
        """
        stats = {
            'forums': [],
            'threads_count': 0,
            'posts_count': 0
        }
        
        forums_result = self.get_forums()
        if forums_result.get('success'):
            forums_data = forums_result.get('data', {}).get('forums', [])
            stats['forums'] = forums_data
            stats['forums_count'] = len(forums_data)
        
        return stats
