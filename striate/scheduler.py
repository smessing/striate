class Scheduler:
  @staticmethod
  def makeScheduler(alg, trainer):
    if alg == 'smooth':
      return SmoothScheduler(trainer)
    
    if alg == 'increment':
      return IncrementScheduler(trainer)

  def __init__(self, trainer):
    self.trainer = trainer
    assert self.trainer.test_freq == self.trainer.save_freq, 'the save freq must be equal to test freq'
    assert len(self.trainer.test_range) == 1, 'the test set could only have one batch'

  def check_continue_trainning(self):
    return True

  def check_test_data(self):
    return True

  def check_save_checkpoint(self):
    return True

class SmoothScheduler(Scheduler):
  def __init__(self, trainer):
    Scheduler.__init__(self, trainer)
    self.test_accu = []
    self.step = 5
    self.prev_avg = 0.0
    self.num_test_outputs = 0
    self.keep = True

  def check_continue_trainning(self):
    return self.keep

  def check_save_checkpoint(self):
    if self.trainer.test_outputs == []:
      return True
    num = len(self.trainer.test_outputs)
    if num != self.num_test_outputs:
      self.num_test_outputs = num
      self.test_accu.append(1 - self.trainer.test_outputs[-1][0]['logprob'][1])
      if len(self.test_accu) <= self.step:
        self.keep = True
      else:
        avg = sum(self.test_accu[-(1 + self.step) : -1]) / self.step

        if avg < self.prev_avg:
          self.keep = False
        else:
          self.keep = True
          self.prev_avg = avg
    return self.keep

class IncrementScheduler(Scheduler):
  def __init__(self, trainer):
    Scheduler.__init__(self, trainer)
