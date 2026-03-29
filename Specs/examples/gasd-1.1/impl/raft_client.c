#include "raft.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void print_status(RaftNode *node) {
  printf("\n--- RAFT NODE STATUS ---\n");
  printf("State:      %s\n", raft_get_state_name(node->state));
  printf("Term:       %d\n", node->current_term);
  printf("Voted For:  %d\n", node->voted_for);
  printf("Votes Got:  %d/%d\n", node->votes_received, node->cluster_size);
  printf("Log Size:   %d\n", node->log_count);
  printf("------------------------\n\n");
}

void run_slow_simulation(RaftNode *node) {
  printf("\n>>> RAFT CONVERGENCE SIMULATION STARTING <<<\n");

  // Reset state
  node->current_term = 0;
  node->state = FOLLOWER;
  node->voted_for = -1;
  node->votes_received = 0;

  printf("[Step 1] Node initialized as FOLLOWER (Term 0)\n");
  printf("          Waiting for election timeout...\n");
  usleep(1200000);

  printf("\n[Step 2] Timeout reached! Starting election...\n");
  raft_start_election(node);
  usleep(1500000);

  if (node->state == LEADER) {
    printf("\n[Step 3] Converged to LEADER for Term %d.\n", node->current_term);
    printf("          Maintaining authority with periodic heartbeats...\n");
    for (int i = 0; i < 3; i++) {
      printf("  > Heartbeat %d sent\n", i + 1);
      usleep(800000);
    }
  }

  int higher_term = node->current_term + 2;
  printf("\n[Step 4] Network event: A higher term (Term %d) message arrives!\n",
         higher_term);
  printf("          Simulating incoming HEARTBEAT from new leader...\n");
  usleep(1000000);

  Message msg = {.type = HEARTBEAT, .term = higher_term};
  raft_handle_message(node, msg);
  usleep(1200000);

  printf("\n[Step 5] Finalizing convergence check...\n");
  usleep(800000);

  printf("\n>>> SIMULATION COMPLETE <<<\n");
  print_status(node);
}

void print_help() {
  printf("Commands:\n");
  printf("  status            - Show current node state\n");
  printf("  election          - Trigger a new election cycle\n");
  printf("  simulate          - Run a slow simulation of Raft convergence\n");
  printf("  msg hb <term>     - Simulate receiving a Heartbeat message\n");
  printf("  msg vote <term>   - Simulate receiving a RequestVote message\n");
  printf("  msg append <term> - Simulate receiving an AppendEntries message\n");
  printf("  help              - Show this help\n");
  printf("  exit              - Exit the client\n");
}

int main() {
  RaftNode node = {.current_term = 0,
                   .state = FOLLOWER,
                   .votes_received = 0,
                   .cluster_size = 500,
                   .voted_for = -1,
                   .log_count = 0};

  char line[256];
  printf("Raft Interactive Test Client\n");
  printf("Type 'help' for commands.\n");

  while (1) {
    printf("raft> ");
    if (!fgets(line, sizeof(line), stdin))
      break;
    line[strcspn(line, "\n")] = 0;

    char *cmd = strtok(line, " ");
    if (!cmd)
      continue;

    if (strcmp(cmd, "exit") == 0) {
      break;
    } else if (strcmp(cmd, "help") == 0) {
      print_help();
    } else if (strcmp(cmd, "status") == 0) {
      print_status(&node);
    } else if (strcmp(cmd, "simulate") == 0) {
      run_slow_simulation(&node);
    } else if (strcmp(cmd, "election") == 0) {
      raft_start_election(&node);
    } else if (strcmp(cmd, "msg") == 0) {
      char *type_str = strtok(NULL, " ");
      char *term_str = strtok(NULL, " ");

      if (!type_str || !term_str) {
        printf("Error: msg requires type (hb|vote|append) and term\n");
        continue;
      }

      int term = atoi(term_str);
      Message msg = {.term = term};

      if (strcmp(type_str, "hb") == 0)
        msg.type = HEARTBEAT;
      else if (strcmp(type_str, "vote") == 0)
        msg.type = REQUEST_VOTE;
      else if (strcmp(type_str, "append") == 0)
        msg.type = APPEND_ENTRIES;
      else {
        printf("Error: unknown message type %s\n", type_str);
        continue;
      }

      Response resp = raft_handle_message(&node, msg);
      printf("Message processed. Response: success=%d, current_term=%d\n",
             resp.success, resp.term);
    } else {
      printf("Unknown command: %s. Type 'help'.\n", cmd);
    }
  }

  return 0;
}
