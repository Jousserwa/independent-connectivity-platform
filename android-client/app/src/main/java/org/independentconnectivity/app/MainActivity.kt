package org.independentconnectivity.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme(colorScheme = lightColorScheme()) {
                Surface(modifier = Modifier.fillMaxSize()) {
                    ConnectivityHome()
                }
            }
        }
    }
}

@Composable
private fun ConnectivityHome() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Independent Connectivity",
            style = MaterialTheme.typography.headlineSmall
        )
        Text(
            text = "A simpler way to connect through authorized community and internet gateways.",
            style = MaterialTheme.typography.bodyMedium
        )

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(18.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text("Connection status", style = MaterialTheme.typography.titleMedium)
                Text("Not connected", style = MaterialTheme.typography.headlineSmall)
                Text(
                    "The first local gateway has not been configured yet. This build is an interface foundation, not an active VPN."
                )
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Gateway:")
            Text("Not configured", color = MaterialTheme.colorScheme.secondary)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Access pass:")
            Text("No test entitlement", color = MaterialTheme.colorScheme.secondary)
        }

        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { /* Connection flow is added after the control plane and gateway are tested. */ },
            enabled = false,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Connect — gateway not ready")
        }
        Text(
            text = "This prototype will only connect to networks and gateways that are authorized for the service. A VPN does not create free mobile data or bypass an operator's billing.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.secondary
        )
    }
}
