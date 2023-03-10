import pytest
from brownie import Ballot, accounts, convert, reverts


proposals = [1007, 1014, 1021]


@pytest.fixture
def ballot(scope="module"):
    byte_proposals = [convert.to_bytes(p) for p in proposals]
    return Ballot.deploy(byte_proposals, {"from": accounts[0], "gas_price": "60 gwei"})


def test_correct_chairperson(ballot):
    assert ballot.chairperson() == accounts[0]


def test_has_proposals(ballot):
    assert convert.to_int(ballot.proposals(0)[0]) == proposals[0]
    assert convert.to_int(ballot.proposals(1)[0]) == proposals[1]
    assert convert.to_int(ballot.proposals(2)[0]) == proposals[2]


def test_rights_to_vote_admin(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    _, _, weight, _ = ballot.voters(accounts[1])
    assert weight == 1


def test_rights_to_vote_nonadmin(ballot):
    with reverts():
        ballot.rightToVote(accounts[2], {"from": accounts[1], "gas_price": "60 gwei"})
    assert ballot.voters(accounts[2])[2] == 0

def test_rights_to_vote_hasvoted(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.vote(0, {"from": accounts[1], "gas_price": "60 gwei"})
    with reverts():
        ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})

def test_rights_to_vote_hasrights(ballot):
    with reverts():
        ballot.rightToVote(accounts[0], {"from": accounts[0], "gas_price": "60 gwei"})
    
    ballot.rightToVote(accounts[1], {"from": accounts[0]})
    with reverts():
        ballot.rightToVote(accounts[1], {"from": accounts[0]})


def test_delegate_has_voted(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[5], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.vote(0, {"from": accounts[1], "gas_price": "60 gwei"})
    
    with reverts():
        ballot.delegate(accounts[5], {"from": accounts[1], "gas_price": "60 gwei"})

def test_delegate_toself(ballot):
    ballot.delegate(accounts[0], {"from": accounts[0], "gas_price": "60 gwei"})

def test_delegates_toloop(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[2], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.delegate(accounts[2], {"from": accounts[1], "gas_price": "60 gwei"})

    with reverts():
        ballot.delegate(accounts[1], {"from": accounts[2], "gas_price": "60 gwei"})

def test_delegate_weight(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    with reverts():
        ballot.delegate(accounts[2], {"from": accounts[1], "gas_price": "60 gwei"})

def test_delegate_sender_vote(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[2], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.delegate(accounts[2], {"from": accounts[1], "gas_price": "60 gwei"})
    assert ballot.voters(accounts[2])[0] != convert.datatypes.EthAddress("0x0")

        



def test_delegates_success_setstate(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[2], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.delegate(accounts[2], {"from": accounts[1], "gas_price": "60 gwei"})
    delegate, vote, weight, voted = ballot.voters(accounts[1])
    assert voted == True
    assert delegate == accounts[2]

def test_delegates_success_notvoted(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[2], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[3], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.delegate(accounts[3], {"from": accounts[1], "gas_price": "60 gwei"})
    ballot.delegate(accounts[3], {"from": accounts[2], "gas_price": "60 gwei"})
    _, _, weight, _ = ballot.voters(accounts[3])
    assert weight == 3

def test_delegates_success_hasvoted(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[2], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[3], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.vote(0, {"from": accounts[2], "gas_price": "60 gwei"})
    ballot.delegate(accounts[2], {"from": accounts[1], "gas_price": "60 gwei"})
    ballot.delegate(accounts[2], {"from": accounts[3], "gas_price": "60 gwei"})
    _, voteCount = ballot.proposals(0)
    assert voteCount == 3

def test_winning_VoteCount(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[2], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.rightToVote(accounts[3], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.vote(0, {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.vote(0, {"from": accounts[1], "gas_price": "60 gwei"})
    ballot.vote(0, {"from": accounts[2], "gas_price": "60 gwei"})
    assert ballot.winningProposal() == 0

def test_vote(ballot):
    ballot.rightToVote(accounts[1], {"from": accounts[0], "gas_price": "60 gwei"})
    ballot.vote(0, {"from": accounts[1], "gas_price": "60 gwei"})
    with reverts():
        ballot.vote(0, {"from": accounts[1], "gas_price": "60 gwei"})  