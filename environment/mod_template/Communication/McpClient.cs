using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace StardewAIAgent.Communication
{
    public class McpClient
    {
        private static readonly HttpClient client = new HttpClient();
        private readonly string _serverUrl;

        public McpClient(string serverUrl)
        {
            _serverUrl = serverUrl;
        }

        public async Task<string> SendStateAsync(object state)
        {
            try
            {
                var json = JsonConvert.SerializeObject(state);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await client.PostAsync($"{_serverUrl}/state", content);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadAsStringAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error sending state: {ex.Message}");
                return null;
            }
        }

        public async Task<string> GetDecisionAsync()
        {
            try
            {
                var response = await client.GetAsync($"{_serverUrl}/decision");
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadAsStringAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting decision: {ex.Message}");
                return null;
            }
        }
    }
}