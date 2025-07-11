
import { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Bot, Send, User, Loader2, FileText, AlertTriangle } from "lucide-react";
import { apiService, AIResponse } from "@/services";
import { toast } from "sonner";

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  metadata?: {
    clinical_analysis?: boolean;
    tools_used?: boolean;
    workflow_executed?: boolean;
  };
}

const predefinedQueries = [
  "Analyze critical anemia finding for CARD001",
  "Review blood pressure discrepancy for CARD002", 
  "Check clean subjects CARD003, CARD007 for quality verification",
  "Assess protocol violations for subjects CARD010, CARD030",
  "Generate safety report for problem subjects CARD005, CARD006",
  "Check protocol compliance for Week 4 visits"
];

export default function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: '🤖 **Clinical Portfolio Manager Ready**\n\nI can help you analyze real clinical data from your 50 cardiology subjects (CARD001-CARD050). I have access to:\n\n• Complete clinical profiles with demographics, vital signs, and lab values\n• Real discrepancy detection between EDC and source documents\n• Medical interpretation of cardiovascular and renal markers\n• Clinical recommendations for safety monitoring\n\nHow can I assist with your clinical analysis today?',
      timestamp: new Date(),
      metadata: { clinical_analysis: true }
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Check backend health on component mount
  useEffect(() => {
    apiService.checkHealth()
      .then(() => {
        setBackendStatus('online');
        console.log('✅ Backend is online');
      })
      .catch(() => {
        setBackendStatus('offline');
        console.log('❌ Backend is offline');
      });
  }, []);

  const chatMutation = useMutation({
    mutationFn: (message: string) => apiService.sendChatMessage(message),
    onSuccess: (response: AIResponse) => {
      const aiMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'ai',
        content: response.response,
        timestamp: new Date(),
        metadata: response.metadata
      };
      setMessages(prev => [...prev, aiMessage]);
    },
    onError: (error) => {
      toast.error("Failed to get AI response. Please try again.");
      console.error('Chat error:', error);
    }
  });

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    chatMutation.mutate(inputMessage);
    setInputMessage('');
  };

  const handlePredefinedQuery = (query: string) => {
    setInputMessage(query);
  };

  const formatAIResponse = (content: string) => {
    // Simple markdown-like formatting for clinical responses
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/CLINICAL FINDING:/g, '<strong style="color: #dc2626;">CLINICAL FINDING:</strong>')
      .replace(/CLINICAL SIGNIFICANCE:/g, '<strong style="color: #ea580c;">CLINICAL SIGNIFICANCE:</strong>')
      .replace(/RECOMMENDED ACTION:/g, '<strong style="color: #059669;">RECOMMENDED ACTION:</strong>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <Bot className="h-8 w-8 text-blue-600" />
            AI Clinical Portfolio Manager
          </h1>
          <p className="text-slate-600 mt-1">
            Interactive clinical analysis powered by OpenAI Agents SDK
          </p>
        </div>
        <Badge 
          variant="outline" 
          className={
            backendStatus === 'online' 
              ? "bg-green-50 text-green-700 border-green-200"
              : backendStatus === 'offline'
              ? "bg-red-50 text-red-700 border-red-200"
              : "bg-yellow-50 text-yellow-700 border-yellow-200"
          }
        >
          ● {backendStatus === 'online' ? 'Agent Active' : backendStatus === 'offline' ? 'Agent Offline' : 'Checking...'}
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Interface */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-blue-600" />
              Clinical Analysis Chat
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Messages */}
            <div className="space-y-4 max-h-96 overflow-y-auto mb-4 p-4 bg-slate-50 rounded-lg">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex gap-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className={`p-2 rounded-full ${message.type === 'user' ? 'bg-blue-600' : 'bg-slate-600'}`}>
                      {message.type === 'user' ? (
                        <User className="h-4 w-4 text-white" />
                      ) : (
                        <Bot className="h-4 w-4 text-white" />
                      )}
                    </div>
                    <div className={`p-4 rounded-lg ${
                      message.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-white border border-slate-200'
                    }`}>
                      {message.type === 'ai' ? (
                        <div 
                          dangerouslySetInnerHTML={{ 
                            __html: formatAIResponse(message.content) 
                          }} 
                        />
                      ) : (
                        <p>{message.content}</p>
                      )}
                      
                      {message.metadata && (
                        <div className="flex gap-2 mt-3 pt-2 border-t border-slate-100">
                          {message.metadata.clinical_analysis && (
                            <Badge variant="secondary" className="text-xs">
                              <AlertTriangle className="h-3 w-3 mr-1" />
                              Clinical Analysis
                            </Badge>
                          )}
                          {message.metadata.tools_used && (
                            <Badge variant="outline" className="text-xs">
                              Tools Used
                            </Badge>
                          )}
                        </div>
                      )}
                      
                      <div className="text-xs text-slate-500 mt-2">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {chatMutation.isPending && (
                <div className="flex gap-3 justify-start">
                  <div className="flex gap-2">
                    <div className="p-2 rounded-full bg-slate-600">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="p-4 bg-white border border-slate-200 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Analyzing clinical data...
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="flex gap-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about clinical data, subjects, or analysis..."
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                className="flex-1"
              />
              <Button 
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || chatMutation.isPending}
              >
                {chatMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick Clinical Queries</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {predefinedQueries.map((query, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => handlePredefinedQuery(query)}
                className="w-full text-left justify-start h-auto p-2 text-xs"
              >
                {query}
              </Button>
            ))}
            
            <div className="pt-4 border-t">
              <p className="text-xs text-slate-600 mb-2">Agent Capabilities:</p>
              <div className="space-y-1">
                <Badge variant="outline" className="text-xs">Real Clinical Data</Badge>
                <Badge variant="outline" className="text-xs">Medical Interpretation</Badge>
                <Badge variant="outline" className="text-xs">Safety Monitoring</Badge>
                <Badge variant="outline" className="text-xs">Workflow Orchestration</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
