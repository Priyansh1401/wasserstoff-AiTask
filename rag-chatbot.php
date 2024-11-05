<?php
/**
 * Plugin Name: RAG Chatbot
 * Description: A RAG-based Query Suggestion Chatbot with Chain of Thought
 * Version: 1.0
 * Author: Your Name
 */

if (!defined('ABSPATH')) {
    exit;
}

class RAGChatbot {
    private $api_url = 'http://localhost:8000';  // Change this to your API endpoint

    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_ajax_rag_chatbot_query', array($this, 'handle_query'));
        add_action('wp_ajax_nopriv_rag_chatbot_query', array($this, 'handle_query'));
        add_action('save_post', array($this, 'handle_content_update'), 10, 3);
        add_action('wp_footer', array($this, 'render_chat_interface'));
    }

    public function init() {
        // Initialize plugin
        $this->register_content_types();
    }

    public function register_content_types() {
        // Register custom post types if needed
    }

    public function enqueue_scripts() {
        wp_enqueue_style(
            'rag-chatbot-style',
            plugins_url('assets/css/chatbot.css', __FILE__),
            array(),
            '1.0.0'
        );

        wp_enqueue_script(
            'rag-chatbot-script',
            plugins_url('assets/js/chatbot.js', __FILE__),
            array('jquery'),
            '1.0.0',
            true
        );

        wp_localize_script('rag-chatbot-script', 'ragChatbot', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('rag-chatbot-nonce')
        ));
    }

    public function handle_query() {
        check_ajax_referer('rag-chatbot-nonce', 'nonce');

        $query = sanitize_text_field($_POST['query']);
        $context = isset($_POST['context']) ? array_map('sanitize_text_field', $_POST['context']) : array();

        $response = wp_remote_post($this->api_url . '/query', array(
            'headers' => array(
                'Content-Type' => 'application/json'
            ),
            'body' => json_encode(array(
                'text' => $query,
                'context' => $context
            ))
        ));

        if (is_wp_error($response)) {
            wp_send_json_error('Error processing query');
            return;
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        wp_send_json_success($body);
    }

    public function handle_content_update($post_id, $post, $update) {
        if (wp_is_post_revision($post_id)) {
            return;
        }

        $content = array(
            'id' => (string)$post_id,
            'text' => wp_strip_all_tags($post->post_content),
            'metadata' => array(
                'title' => $post->post_title,
                'type' => $post->post_type,
                'url' => get_permalink($post_id)
            )
        );

        wp_remote_post($this->api_url . '/content', array(
            'headers' => array(
                'Content-Type' => 'application/json'
            ),
            'body' => json_encode($content)
        ));
    }

    public function render_chat_interface() {
        ?>
        <div id="rag-chatbot-container" class="rag-chatbot-container">
            <div id="rag-chatbot-header" class="rag-chatbot-header">
                <h3>Chat Assistant</h3>
                <button id="rag-chatbot-toggle">×</button>
            </div>
            <div id="rag-chatbot-messages" class="rag-chatbot-messages"></div>
            <div id="rag-chatbot-input-container" class="rag-chatbot-input-container">
                <textarea id="rag-chatbot-input" placeholder="Type your question..."></textarea>
                <button id="rag-chatbot-send">Send</button>
            </div>
        </div>
        <?php
    }
}

// Initialize the plugin
new RAGChatbot();