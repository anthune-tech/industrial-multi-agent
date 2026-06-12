interface ChatBubbleProps {
  role: 'user' | 'agent'
  text: string
}

export default function ChatBubble({ role, text }: ChatBubbleProps) {
  const isUser = role === 'user'
  return (
    <div style={{
      display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 8,
    }}>
      <div style={{
        maxWidth: '70%',
        padding: '8px 14px',
        borderRadius: 12,
        background: isUser ? '#1a73e8' : '#e8eaed',
        color: isUser ? '#fff' : '#333',
        fontSize: 14,
        lineHeight: 1.5,
        whiteSpace: 'pre-wrap',
      }}>
        {text}
      </div>
    </div>
  )
}
