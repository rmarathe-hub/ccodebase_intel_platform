package com.example.users;

import com.example.common.BaseController;
import com.example.users.api.UserApi;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/users")
public class UserController extends BaseController implements UserApi {
  @GetMapping("/{id}")
  public String get(@PathVariable String id) {
    return id;
  }
}
