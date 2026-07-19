package com.example.auth;

import java.util.List;
import com.example.users.User;

public class AuthService {
  private final UserRepository users;
  public static final String NAME = "auth";

  public AuthService(UserRepository users) {
    this.users = users;
  }

  public boolean login(String user, String password) {
    return users != null;
  }

  private <R> R identity(R value) {
    return value;
  }
}
