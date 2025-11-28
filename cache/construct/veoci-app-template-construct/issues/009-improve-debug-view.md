# Enhance debug view with configuration diagnostics

**Type:** `issue`
**Labels:** `identity:smith`, `enhancement`, `dx`

## Context

From Construct review of `veoci-app-template-construct`. Persephone and Seraph noted the debug view is underutilized.

**Source:** `~/.matrix/cache/construct/veoci-app-template-construct/devex-review.md`

## Problem

A `/debug` route exists but doesn't help diagnose common issues:
- Is VEOCI_API_URL configured correctly?
- Is the API reachable?
- Is the user authenticated?
- What's in localStorage?

Developers debugging issues have to manually inspect DevTools instead of using a built-in diagnostic panel.

## Solution

Enhance the debug view to show configuration status and common diagnostics.

## Implementation Steps

1. Update `src/views/DebugView.vue` to include:

   **API Configuration Section:**
   - Display current `VEOCI_API_URL` value
   - Show connection status (reachable/unreachable)
   - Test button to ping API health endpoint

   **Auth State Section:**
   - Is authenticated: yes/no
   - Token present: yes/no (don't show actual token)
   - Token expiry time (decoded from JWT)
   - Refresh token status

   **localStorage Section:**
   - List all keys
   - Show values (redact sensitive ones like tokens)
   - Clear button for debugging

   **Environment Section:**
   - Current mode (development/production)
   - VeociJS SDK version
   - Build timestamp

2. Example structure:
   ```vue
   <template>
     <v-container>
       <h1>Debug Panel</h1>

       <v-card class="mb-4">
         <v-card-title>API Configuration</v-card-title>
         <v-card-text>
           <v-table density="compact">
             <tbody>
               <tr>
                 <td>API URL</td>
                 <td><code>{{ apiUrl || 'NOT SET' }}</code></td>
                 <td>
                   <v-chip :color="apiStatus" size="small">
                     {{ apiStatusText }}
                   </v-chip>
                 </td>
               </tr>
             </tbody>
           </v-table>
           <v-btn @click="testConnection" class="mt-2">
             Test Connection
           </v-btn>
         </v-card-text>
       </v-card>

       <!-- Auth State, localStorage, Environment sections... -->
     </v-container>
   </template>
   ```

3. Add route guard to only show in development:
   ```typescript
   {
     path: '/debug',
     component: DebugView,
     beforeEnter: () => {
       if (import.meta.env.PROD) {
         return { path: '/' }
       }
     }
   }
   ```

## Acceptance Criteria

- [ ] Debug view shows API URL and connection status
- [ ] Debug view shows auth state (without exposing tokens)
- [ ] Debug view shows localStorage contents (redacted)
- [ ] "Test Connection" button verifies API reachability
- [ ] Debug view only accessible in development mode
- [ ] Helps diagnose common issues in <1 minute

## Handoff

Smith implements. Persephone reviews UX. Seraph verifies it helps first-run debugging.
