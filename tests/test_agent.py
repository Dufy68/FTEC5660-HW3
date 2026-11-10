"""Offline checks for evidence validation and company-level error isolation."""
import asyncio
import unittest
from unittest.mock import AsyncMock, patch
import hw3


def payload():
    return {'assessments': [
        {'point': p, 'verdict': 'PASS', 'quote': f'evidence {p}', 'reason': 'Supported.'}
        for p in hw3.CHOSEN_POINTS
    ]}


class FakeInterview:
    name = 'interview'

    def __init__(self):
        self.calls = []

    async def ainvoke(self, args):
        self.calls.append(args)
        p = next(p for p, (role, topic) in hw3.INTERVIEW_PLAN.items()
                 if args == {'role': role, 'topic': topic})
        return f'The witness says evidence {p}.'


class AgentTests(unittest.IsolatedAsyncioTestCase):
    def test_wrong_source_quote_and_duplicate_point_rejected(self):
        evidence = {p: f'evidence {p}' for p in hw3.CHOSEN_POINTS}
        data = payload()
        data['assessments'][0]['quote'] = 'evidence 7'
        with self.assertRaises(ValueError):
            hw3.validate_assessments(data, evidence)
        data = payload()
        data['assessments'][1]['point'] = 4
        with self.assertRaises(ValueError):
            hw3.validate_assessments(data, evidence)

    async def test_retry_does_not_repeat_interviews(self):
        interview = FakeInterview()
        model = AsyncMock()
        model.ainvoke.side_effect = [ValueError('invalid JSON'), payload()]
        with patch.object(asyncio, 'sleep', new=AsyncMock()):
            result = await hw3.analyze_companies(model, {'arbitrary_folder': [interview]})
        self.assertEqual(len(interview.calls), 3)
        self.assertEqual(model.ainvoke.await_count, 2)
        self.assertEqual(result['arbitrary_folder']['points'], {4: 'PASS', 7: 'PASS', 11: 'PASS'})

    async def test_company_failure_preserves_other_result(self):
        class BrokenInterview(FakeInterview):
            async def ainvoke(self, args):
                raise RuntimeError('tool failure')
        model = AsyncMock()
        model.ainvoke.return_value = payload()
        result = await hw3.analyze_companies(model, {
            'broken': [BrokenInterview()], 'healthy': [FakeInterview()]})
        self.assertEqual(result['broken']['points'], {})
        self.assertEqual(len(result['healthy']['points']), 3)

    async def test_exhausted_api_retries_return_diagnostic(self):
        model = AsyncMock()
        model.ainvoke.side_effect = RuntimeError('provider failure')
        interview = FakeInterview()
        with patch.object(asyncio, 'sleep', new=AsyncMock()):
            result = await hw3.analyze_companies(model, {'x': [interview]})
        self.assertEqual(model.ainvoke.await_count, 3)
        self.assertEqual(len(interview.calls), 3)
        self.assertEqual(result['x']['points'], {})
        self.assertIn('unavailable', result['x']['summary'])


if __name__ == '__main__':
    unittest.main()
